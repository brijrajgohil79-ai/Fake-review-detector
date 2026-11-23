"""
Machine Learning Training Module for Fake Review Trap.
Trains a TF-IDF + Logistic Regression model on labeled review examples
and saves the artifacts for hybrid inference.
"""

import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, "review_classifier.joblib")

# Curated dataset of genuine (0) and fake (1) reviews for calibration
DATASET = [
    # --- FAKE REVIEWS (1) ---
    ("BEST PRODUCT EVER BUY NOW!!! MUST BUY DO NOT HESITATE 10/10 FIVE STARS WORKS LIKE MAGIC LIFE CHANGER", 1),
    ("Superb quality item! Don't miss out, use promo code DISCOUNT50 for 50% cashback on https://super-deals.shop or contact WhatsApp +1-555-0199 for bulk discounts!", 1),
    ("This is hands down the most amazing, flawless, and wonderful product I have ever purchased. Absolute perfection in every detail and brilliant craftsmanship!", 1),
    ("good good good product very nice nice nice good item fast fast delivery good", 1),
    ("AMAZING AMAZING BUY BUY BUY CLICK LINK FOR COUPON WWW.DEALS.ONLINE", 1),
    ("Works like a charm! 5 stars! Great product highly recommended to everyone must buy blindly go for it!", 1),
    ("Never seen anything better in my life! Miracle product buy immediately!", 1),
    ("Value for money product! Completely in love! Five stars!", 1),
    ("BEST BUY OF THE CENTURY! Treat yourself and get 10 of these right now!", 1),
    ("Contact me on telegram @dealmaster for 40% discount coupon voucher code", 1),
    ("A+++++ seller very fast shipping item as described five stars recommended to all buyers", 1),
    ("Best quality best price best service best ever buy this now!!!", 1),
    ("Unbelievable result overnight miracle worker game changer run dont walk!", 1),
    ("Super item superb very nice excellent excellent excellent 100% genuine guaranteed", 1),
    ("Check out our site http://discount-hub.net for free gift vouchers with purchase!", 1),
    ("Great! Loved it! Awesome! Beautiful! Outstanding! Perfect!", 1),
    ("Life changing purchase don't think twice just add to cart immediately five stars", 1),
    ("10/10 would buy again and again everyone in my family ordered one!", 1),
    ("MUST BUY DO NOT MISS THIS OPPORTUNITY BEST ITEM ON THE MARKET TODAY", 1),
    ("Call 800-555-0144 to claim free warranty or email support@fastrebates.io", 1),
    ("Sooooo amazinggggg loved it so so much five stars best purchase ever!", 1),
    ("Pure perfection! Zero complaints! Everything is flawless! Buy buy buy!", 1),
    ("Nice nice nice nice nice good quality product fast delivery very nice", 1),
    ("Best product in the world. Ten out of ten stars. You must purchase right now.", 1),

    # --- GENUINE REVIEWS (0) ---
    ("I have been using these wireless headphones daily for about 3 weeks. The sound quality is crisp and the bass is solid for this price point. Battery life comfortably lasts 28 hours on a single charge. However, the plastic ear cups can get slightly warm after 2 hours of continuous wear. Overall, very satisfied with this upgrade compared to my previous pair.", 0),
    ("The keyboard has good mechanical switches with responsive tactile feedback. Aluminum frame feels solid and durable. Only complaint is the USB cable is quite stiff and took effort to route behind my desk.", 0),
    ("Bought this blender for morning smoothies. Crushes ice and frozen fruit easily within 30 seconds. It is somewhat louder than my previous 500W model, but cleanup is quick under running warm water.", 0),
    ("The cotton fabric is breathable and stitched neatly with no loose threads. Fit is true to size around the shoulders, although the sleeves run about half an inch longer than standard medium sizing.", 0),
    ("Setup was straightforward using the included instructions and bracket screws. Display resolution is sharp at 1080p, but maximum brightness is mediocre in direct sunlight. Great secondary monitor for the price.", 0),
    ("After 2 months of daily use, the battery still holds charge for 3 to 4 days of moderate tracking. The silicone strap does attract lint occasionally, but the heart rate sensor has been accurate compared to my chest strap.", 0),
    ("The package arrived 2 days earlier than scheduled. The ceramic mug is thick and keeps coffee warm for about 45 minutes without a lid. Nice comfortable handle grip.", 0),
    ("Decent laptop backpack with plenty of compartments for a 15-inch laptop, charger, and notebook. The water bottle side pocket is slightly tight for a 32oz hydroflask, but the zippers feel durable.", 0),
    ("Audio clarity during Zoom calls is clear with minimal background noise picked up by the microphone. Earbuds fit comfortably without falling out during light jogging.", 0),
    ("Installed this SSD in my desktop PC last weekend. Read speeds benchmarked at 3400 MB/s which matched the advertised specs. Boot times dropped from 45 seconds to under 12 seconds.", 0),
    ("The non-stick frying pan heats evenly on my induction stove. Eggs slide right off without excess butter. Hand washing is required to preserve the coating, but it wipes clean easily with a sponge.", 0),
    ("The jacket is warm down to around 30 degrees Fahrenheit. The outer shell repels light drizzle well, though the front zipper can snag on the inner flap if pulled quickly.", 0),
    ("Colors are vibrant on the AMOLED panel. Battery takes about 70 minutes to charge from 15% to full with the supplied 30W charger. Fingerprint sensor fails maybe once out of ten attempts.", 0),
    ("Good build quality for entry-level studio monitors. Bass response rolls off below 60Hz so you may need a subwoofer for bass-heavy mixing, but mids and highs are well balanced.", 0),
    ("Lightweight running shoes with adequate arch support. I put 50 miles on them so far on paved trails and tread wear looks minimal. Size up half a size if you have wide feet.", 0),
    ("The cordless vacuum works well on hardwood floors and low-pile rugs. Suction on turbo mode drains the battery in about 12 minutes, but eco mode lasts around 35 minutes which is plenty for my apartment.", 0),
]


def train_and_save():
    texts, labels = zip(*DATASET)

    # Pipeline: TF-IDF with unigrams and bigrams + Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            lowercase=True,
            token_pattern=r"\b[A-Za-z0-9'-]+\b",
            sublinear_tf=True
        )),
        ("clf", LogisticRegression(C=1.5, max_iter=300, random_state=42))
    ])

    pipeline.fit(texts, labels)

    predictions = pipeline.predict(texts)
    acc = accuracy_score(labels, predictions)
    print(f"Model trained successfully. In-sample accuracy: {acc * 100:.1f}%")

    joblib.dump(pipeline, MODEL_FILE)
    print(f"Saved model pipeline to: {MODEL_FILE}")
    return pipeline


if __name__ == "__main__":
    train_and_save()
