"""
Detection logic for Fake Review Trap.
Analyzes reviews using a hybrid rule-based engine, lexical metrics, sentiment verification,
and feature-grounding heuristics.
"""

import re
import os
import math
from typing import Dict, Any, List, Optional, Tuple

# Optional Machine Learning Classifier Pipeline
ML_PIPELINE = None
try:
    import joblib
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review_classifier.joblib")
    if os.path.exists(MODEL_PATH):
        ML_PIPELINE = joblib.load(MODEL_PATH)
except Exception:
    ML_PIPELINE = None

# Common generic praise phrases and fake review clichés
GENERIC_PRAISE_PATTERNS = [
    r"\bbest (?:product|purchase|item|thing) ever\b",
    r"\bmust buy\b",
    r"\blife changer\b",
    r"\bgame changer\b",
    r"\bchanged my life\b",
    r"\bworth every penny\b",
    r"\bworks like (?:magic|a charm)\b",
    r"\bhighly recommend(?:ed)? to (?:everyone|all)\b",
    r"\bdo not hesitate to buy\b",
    r"\bdon't hesitate to buy\b",
    r"\b10/10\b",
    r"\bfive stars\b",
    r"\b5/5\b",
    r"\bawesome product\b",
    r"\bsuperb (?:product|quality)\b",
    r"\bgreatest of all time\b",
    r"\bmiracle worker\b",
    r"\bblow your mind\b",
    r"\bbuy this (?:now|immediately)\b",
    r"\brun don'?t walk\b",
    r"\btreat yourself\b",
    r"\bblindly go for it\b",
    r"\bjust go for it\b",
    r"\bvalue for money product\b",
    r"\bcompletely in love\b",
    r"\bnever seen anything better\b",
]

# Promotional indicators: URLs, emails, phone numbers, referral codes
PROMO_PATTERNS = [
    r"https?://\S+",
    r"\bwww\.\S+\b",
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    r"\b(?:use|enter|apply) (?:code|coupon|promo|voucher)\b",
    r"\b(?:discount code|referral code|cashback)\b",
    r"\b(?:whatsapp|telegram|contact me at|call on|inbox me|dm me)\b",
    r"\b(?:click here|check out this link|visit)\b",
]

# Product feature markers indicating authentic grounding
SPECIFIC_FEATURE_KEYWORDS = {
    "battery", "charge", "charger", "cable", "screen", "display", "audio", "sound",
    "bass", "treble", "volume", "plastic", "metal", "aluminum", "weight", "heavy",
    "lightweight", "size", "fit", "small", "large", "dimensions", "inches", "centimeters",
    "material", "fabric", "stitching", "zipper", "button", "keys", "keyboard", "mouse",
    "setup", "install", "installation", "manual", "packaging", "box", "delivery", "shipping",
    "color", "shade", "texture", "durability", "scratch", "waterproof", "software",
    "firmware", "app", "connection", "bluetooth", "wifi", "latency", "heat", "fan",
    "noise", "camera", "lens", "resolution", "odor", "smell", "taste", "grip", "pocket"
}

# Experience & usage markers indicating authentic personal trial
USAGE_EXPERIENCE_PATTERNS = [
    r"\b(?:after|in|for) \d+ (?:days?|weeks?|months?|hours?|years?)\b",
    r"\b(?:daily|every day|everyday|all day)\b",
    r"\b(?:first (?:time|week|month|impression)|initial impression)\b",
    r"\b(?:compared to|upgrading from|replacement for|switched from)\b",
    r"\b(?:pros and cons|downside|minor issue|only flaw|however|although|on the other hand)\b",
    r"\b(?:arrived (?:in|on|safely|damaged)|customer service)\b",
    r"\b(?:tested (?:it|this)|put it to the test|real-world)\b",
]

# Simple sentiment lexicons with polarity weights
POSITIVE_WORDS = {
    "excellent": 2.0, "amazing": 2.0, "superb": 2.0, "fantastic": 2.0, "wonderful": 2.0,
    "outstanding": 2.0, "flawless": 2.0, "brilliant": 2.0, "perfect": 2.0, "love": 1.5,
    "great": 1.5, "awesome": 1.5, "good": 1.0, "nice": 1.0, "happy": 1.0, "pleased": 1.0,
    "satisfied": 1.0, "best": 2.0, "exceptional": 2.0, "impressive": 1.5, "recommend": 1.2
}

NEGATIVE_WORDS = {
    "terrible": 2.0, "horrible": 2.0, "awful": 2.0, "scam": 2.5, "fake": 2.0,
    "defective": 2.0, "broke": 2.0, "broken": 2.0, "waste": 2.0, "useless": 2.0,
    "garbage": 2.0, "worst": 2.5, "poor": 1.5, "disappointing": 1.5, "disappointed": 1.5,
    "bad": 1.0, "hate": 1.5, "refund": 1.5, "failed": 1.5, "unacceptable": 2.0,
    "cheaply": 1.5, "junk": 2.0
}

COMMON_ACRONYMS = {"USB", "TV", "LED", "OLED", "HDMI", "PC", "USA", "UK", "RAM", "CPU", "GPU", "SSD", "HDD", "RGB", "FPS", "AC", "DC", "AUX"}


def calculate_lexical_metrics(text: str) -> Dict[str, Any]:
    """Calculates word count, caps ratio, exclamation counts, and lexical diversity."""
    words = re.findall(r"\b[A-Za-z0-9'-]+\b", text)
    word_count = len(words)
    char_count = len(text)
    
    # Exclamation & question mark counts
    exclamation_count = text.count("!")
    question_count = text.count("?")
    consecutive_exclamations = bool(re.search(r"!{2,}", text))
    
    # Capitalization metrics
    alpha_chars = [c for c in text if c.isalpha()]
    total_alpha = len(alpha_chars)
    upper_alpha = [c for c in alpha_chars if c.isupper()]
    caps_percentage = (len(upper_alpha) / total_alpha * 100) if total_alpha > 0 else 0.0

    # Upper case words count (excluding single chars and common acronyms)
    all_caps_words = [w for w in words if len(w) > 1 and w.isupper() and w not in COMMON_ACRONYMS]
    caps_word_ratio = (len(all_caps_words) / word_count) if word_count > 0 else 0.0

    # Lexical diversity (Type-Token Ratio)
    unique_words = set(w.lower() for w in words)
    lexical_diversity = (len(unique_words) / word_count) if word_count > 0 else 0.0

    # Repeated sequences (e.g. 'good good good' or 'aaaa')
    repeated_words_found = bool(re.search(r"\b(\w+)\s+\1\b", text, re.IGNORECASE))
    char_elongation_found = bool(re.search(r"([a-zA-Z])\1{3,}", text))

    return {
        "word_count": word_count,
        "char_count": char_count,
        "exclamation_count": exclamation_count,
        "question_count": question_count,
        "consecutive_exclamations": consecutive_exclamations,
        "caps_percentage": round(caps_percentage, 1),
        "caps_word_ratio": round(caps_word_ratio, 2),
        "lexical_diversity": round(lexical_diversity, 2),
        "repeated_words": repeated_words_found,
        "char_elongation": char_elongation_found,
        "words": words,
        "unique_words": unique_words
    }


def analyze_sentiment(words: List[str]) -> Tuple[float, float, float]:
    """
    Computes positive score, negative score, and net sentiment polarity in [-1.0, 1.0].
    """
    pos_score = 0.0
    neg_score = 0.0
    
    for w in words:
        wl = w.lower()
        if wl in POSITIVE_WORDS:
            pos_score += POSITIVE_WORDS[wl]
        if wl in NEGATIVE_WORDS:
            neg_score += NEGATIVE_WORDS[wl]

    total = pos_score + neg_score
    if total == 0:
        polarity = 0.0
    else:
        polarity = (pos_score - neg_score) / (pos_score + neg_score)

    return round(pos_score, 2), round(neg_score, 2), round(polarity, 2)


def evaluate_grounding_and_features(text: str, words: List[str]) -> Dict[str, Any]:
    """Checks for specific product features, usage duration, and balanced critique."""
    words_set = set(w.lower() for w in words)
    features_found = [feat for feat in SPECIFIC_FEATURE_KEYWORDS if feat in words_set]
    
    usage_matches = []
    for pattern in USAGE_EXPERIENCE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            usage_matches.extend(matches)

    return {
        "feature_count": len(features_found),
        "features": features_found[:5],
        "has_usage_context": len(usage_matches) > 0,
        "usage_indicators": usage_matches[:3]
    }


def analyze_review(review: str, rating: Optional[int] = None) -> Dict[str, Any]:
    """
    Main detection function that scores a review and returns verdict, score, and reasons.

    Args:
        review (str): The review text to analyze.
        rating (int, optional): Star rating (1-5).

    Returns:
        dict: {
            "verdict": "Fake" | "Suspicious" | "Genuine",
            "score": int (0-100 risk score),
            "reasons": list of str,
            "details": dict of diagnostic metrics
        }
    """
    cleaned_review = review.strip()
    if not cleaned_review:
        return {
            "verdict": "Suspicious",
            "score": 50,
            "reasons": ["Empty or whitespace-only review text."],
            "details": {}
        }

    metrics = calculate_lexical_metrics(cleaned_review)
    pos_score, neg_score, polarity = analyze_sentiment(metrics["words"])
    grounding = evaluate_grounding_and_features(cleaned_review, metrics["words"])

    score = 0
    reasons: List[str] = []
    positive_signals: List[str] = []

    # 1. ALL CAPS & Exclamation Marks Rule
    if metrics["caps_percentage"] >= 50 and metrics["word_count"] >= 4:
        score += 25
        reasons.append(f"Excessive ALL CAPS detected ({metrics['caps_percentage']}% of letters are capitalized).")
    elif metrics["caps_percentage"] >= 28 and metrics["word_count"] >= 4:
        score += 15
        reasons.append(f"Unusually high capitalization ratio ({metrics['caps_percentage']}%).")
    elif metrics["caps_word_ratio"] >= 0.4 and metrics["word_count"] >= 5:
        score += 15
        reasons.append("High proportion of words written entirely in UPPERCASE.")

    if metrics["consecutive_exclamations"] or metrics["exclamation_count"] >= 4:
        score += 15
        reasons.append(f"Excessive exclamation marks ({metrics['exclamation_count']} exclamation mark(s) detected).")
    elif metrics["exclamation_count"] >= 2 and metrics["word_count"] <= 8:
        score += 10
        reasons.append("Multiple exclamation marks in an unusually short review.")

    # 2. Overly Generic Praise Phrases
    generic_matches = []
    for pat in GENERIC_PRAISE_PATTERNS:
        match = re.search(pat, cleaned_review, re.IGNORECASE)
        if match:
            generic_matches.append(match.group(0))

    if len(generic_matches) >= 2:
        score += 28
        reasons.append(f"Multiple generic hype clichés detected (e.g., '{generic_matches[0]}', '{generic_matches[1]}').")
    elif len(generic_matches) == 1:
        score += 14
        reasons.append(f"Contains generic promotional praise cliché: '{generic_matches[0]}'.")

    # 3. Text Length, Repetition, and Lexical Diversity
    if metrics["word_count"] <= 5:
        score += 20
        reasons.append(f"Very brief review ({metrics['word_count']} words) lacking meaningful context.")
    elif metrics["word_count"] <= 8 and len(generic_matches) >= 1:
        score += 15
        reasons.append("Short review relying solely on superlative praise without product context.")

    # High repetition / Low lexical diversity checks
    if metrics["word_count"] >= 4 and metrics["lexical_diversity"] <= 0.50:
        score += 25
        reasons.append(f"Low lexical diversity ({int(metrics['lexical_diversity']*100)}% unique words); repetitive vocabulary pattern.")
    elif metrics["word_count"] >= 10 and metrics["lexical_diversity"] < 0.60:
        score += 18
        reasons.append(f"Repetitive phrasing ({int(metrics['lexical_diversity']*100)}% unique words).")

    if metrics["repeated_words"]:
        score += 20
        reasons.append("Contains repeated identical words/phrases, indicating spam or copy-pasting.")

    if metrics["char_elongation"]:
        score += 15
        reasons.append("Contains unnatural character stretching/elongation (e.g., 'sooooo', 'greeeat').")

    # 4. Promotional Links, Contacts, and Spam Words
    promo_matches = []
    for pat in PROMO_PATTERNS:
        match = re.search(pat, cleaned_review, re.IGNORECASE)
        if match:
            promo_matches.append(match.group(0))

    if promo_matches:
        score += 40
        reasons.append(f"Contains promotional link, contact info, or voucher code ('{promo_matches[0]}').")

    # 5. Rating vs Sentiment Conflict
    rating_conflict = False
    if rating is not None:
        try:
            rating_val = int(rating)
            if rating_val in (1, 2) and polarity >= 0.4 and pos_score >= 2.0:
                score += 35
                rating_conflict = True
                reasons.append(f"Severe rating-sentiment conflict: Rated {rating_val}-star but text expresses glowing praise (positive polarity {polarity}).")
            elif rating_val in (4, 5) and polarity <= -0.4 and neg_score >= 2.0:
                score += 35
                rating_conflict = True
                reasons.append(f"Severe rating-sentiment conflict: Rated {rating_val}-stars but text expresses harsh criticism (negative polarity {polarity}).")
        except (ValueError, TypeError):
            pass

    # 6. Specificity & Grounding (Lack of details vs Authenticity bonus)
    has_specifics = (grounding["feature_count"] > 0) or grounding["has_usage_context"]
    
    if not has_specifics and metrics["word_count"] >= 8 and (len(generic_matches) > 0 or score > 15):
        score += 16
        reasons.append("Lacks specific product details: mentions no physical features, usage conditions, or distinct experience.")
    elif not has_specifics and metrics["word_count"] >= 15 and score == 0:
        # Mild observation if moderate length with zero concrete features
        reasons.append("Notice: Review speaks in broad terms with limited concrete feature mentions.")

    # Authenticity Bonus: Reward reviews with concrete, balanced features
    if has_specifics and not promo_matches and not rating_conflict:
        bonus = 0
        if grounding["feature_count"] >= 2:
            bonus += 15
            positive_signals.append(f"Mentions concrete product characteristics ({', '.join(grounding['features'][:3])}).")
        elif grounding["feature_count"] == 1:
            bonus += 8
            positive_signals.append(f"Mentions product attribute '{grounding['features'][0]}'.")

        if grounding["has_usage_context"]:
            bonus += 12
            positive_signals.append("Includes realistic real-world usage duration or balanced critique.")

        if metrics["lexical_diversity"] >= 0.70 and metrics["word_count"] >= 12:
            bonus += 8
            positive_signals.append("High vocabulary diversity and natural syntactic variation.")

        score = max(0, score - bonus)

    # Calculate base rule-based score (clamped 0-100)
    rule_score = max(0, min(100, int(round(score))))
    ml_active = False
    ml_fake_score = None

    # Optional ML inference (TF-IDF + Logistic Regression)
    if ML_PIPELINE is not None:
        try:
            probs = ML_PIPELINE.predict_proba([cleaned_review])[0]
            ml_prob = float(probs[1])
            ml_fake_score = int(round(ml_prob * 100))
            ml_active = True

            # Hybrid blend: 75% rule-based + 25% ML
            final_score = int(round(0.75 * rule_score + 0.25 * ml_fake_score))

            if ml_fake_score >= 65 and rule_score >= 40:
                reasons.append(f"ML Classifier corroborates high likelihood of synthetic/manipulated text ({ml_fake_score}% risk probability).")
            elif ml_fake_score <= 25 and rule_score <= 30:
                positive_signals.append(f"TF-IDF model predicts natural phrasing ({100 - ml_fake_score}% authenticity probability).")
        except Exception:
            final_score = rule_score
    else:
        final_score = rule_score

    final_score = max(0, min(100, final_score))

    # Determine Verdict
    if final_score >= 65:
        verdict = "Fake"
    elif final_score >= 35:
        verdict = "Suspicious"
    else:
        verdict = "Genuine"

    # If genuine or no suspicious reasons were flagged, provide reassuring notes
    if not reasons:
        if positive_signals:
            reasons = [f"Authentic pattern: {sig}" for sig in positive_signals]
        else:
            reasons = ["Natural tone and balanced vocabulary detected. No suspicious patterns found."]
    elif verdict == "Genuine" and positive_signals:
        reasons.extend([f"Organic indicator: {sig}" for sig in positive_signals])

    details = {
        "word_count": metrics["word_count"],
        "char_count": metrics["char_count"],
        "caps_percentage": metrics["caps_percentage"],
        "exclamation_count": metrics["exclamation_count"],
        "sentiment_polarity": polarity,
        "lexical_diversity": metrics["lexical_diversity"],
        "features_detected": grounding["features"],
        "has_usage_context": grounding["has_usage_context"],
        "rating_conflict": rating_conflict,
        "rule_score": rule_score,
        "ml_active": ml_active,
        "ml_fake_score": ml_fake_score
    }

    return {
        "verdict": verdict,
        "score": final_score,
        "reasons": reasons,
        "details": details
    }
