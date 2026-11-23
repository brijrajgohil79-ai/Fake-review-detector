/**
 * Fake Review Trap - Frontend Application Script
 * Enhanced UI with Speedometer Gauge, Category Breakdowns, Search & Clipboard Tools
 */

document.addEventListener("DOMContentLoaded", () => {
  // Backend base URL (relative works if served via Flask, absolute fallback for standalone browser opening)
  const API_BASE = window.location.origin.includes("5000")
    ? ""
    : "http://127.0.0.1:5000";

  // Preset Sample Reviews for Quick Testing
  const SAMPLES = {
    "fake-hype": {
      rating: 5,
      review: "BEST PRODUCT EVER BUY NOW!!! MUST BUY DO NOT HESITATE TO BUY 10/10 FIVE STARS WORKS LIKE MAGIC LIFE CHANGER!!!"
    },
    "fake-promo": {
      rating: 5,
      review: "Superb quality item! Don't miss out, use promo code DISCOUNT50 for 50% cashback on https://super-deals-shop.online or contact WhatsApp +1-555-0199 for bulk discounts!"
    },
    "fake-mismatch": {
      rating: 1,
      review: "This is hands down the most amazing, flawless, and wonderful product I have ever purchased. Absolute perfection in every detail and brilliant craftsmanship!"
    },
    "suspicious-repeat": {
      rating: 5,
      review: "good good good product very nice nice nice good item fast fast delivery good"
    },
    "genuine-detailed": {
      rating: 4,
      review: "I have been using these wireless headphones daily for about 3 weeks. The sound quality is crisp and the bass is solid for this price point. Battery life comfortably lasts 28 hours on a single charge. However, the plastic ear cups can get slightly warm after 2 hours of continuous wear. Overall, very satisfied with this upgrade compared to my previous pair."
    }
  };

  const STAR_LABELS = {
    1: "★ 1/5 - Poor",
    2: "★★ 2/5 - Fair",
    3: "★★★ 3/5 - Average",
    4: "★★★★ 4/5 - Good",
    5: "★★★★★ 5/5 - Excellent"
  };

  // DOM Elements
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const themeIcon = document.getElementById("themeIcon");
  const themeText = document.getElementById("themeText");

  const analyzeForm = document.getElementById("analyzeForm");
  const reviewInput = document.getElementById("reviewInput");
  const charCountEl = document.getElementById("charCount");
  const wordCountEl = document.getElementById("wordCount");
  const readingTimeEl = document.getElementById("readingTime");
  const submitBtn = document.getElementById("submitBtn");
  const btnText = document.getElementById("btnText");
  const btnSpinner = document.getElementById("btnSpinner");
  const resetBtn = document.getElementById("resetBtn");
  const pasteBtn = document.getElementById("pasteBtn");
  const clearTextBtn = document.getElementById("clearTextBtn");

  const starBtns = document.querySelectorAll(".star-btn");
  const starRatingLabel = document.getElementById("starRatingLabel");
  const clearRatingBtn = document.getElementById("clearRatingBtn");

  const resultsSection = document.getElementById("resultsSection");
  const copyReportBtn = document.getElementById("copyReportBtn");
  const gaugeFill = document.getElementById("gaugeFill");
  const gaugeScore = document.getElementById("gaugeScore");
  const gaugeRiskTag = document.getElementById("gaugeRiskTag");
  const verdictBadge = document.getElementById("verdictBadge");
  const verdictIcon = document.getElementById("verdictIcon");
  const verdictText = document.getElementById("verdictText");
  const verdictSummary = document.getElementById("verdictSummary");
  const meterFill = document.getElementById("meterFill");
  const reasonsList = document.getElementById("reasonsList");

  // Breakdown Bars
  const barScoreCaps = document.getElementById("barScoreCaps");
  const miniBarCaps = document.getElementById("miniBarCaps");
  const barScoreHype = document.getElementById("barScoreHype");
  const miniBarHype = document.getElementById("miniBarHype");
  const barScoreRepetition = document.getElementById("barScoreRepetition");
  const miniBarRepetition = document.getElementById("miniBarRepetition");
  const barScorePromo = document.getElementById("barScorePromo");
  const miniBarPromo = document.getElementById("miniBarPromo");
  const barScoreRating = document.getElementById("barScoreRating");
  const miniBarRating = document.getElementById("miniBarRating");

  // Metrics
  const metricWords = document.getElementById("metricWords");
  const metricCaps = document.getElementById("metricCaps");
  const metricExclamations = document.getElementById("metricExclamations");
  const metricPolarity = document.getElementById("metricPolarity");
  const metricDiversity = document.getElementById("metricDiversity");
  const metricEngine = document.getElementById("metricEngine");

  // History
  const historyList = document.getElementById("historyList");
  const historyCountBadge = document.getElementById("historyCountBadge");
  const historySearchInput = document.getElementById("historySearchInput");
  const filterTabs = document.querySelectorAll(".filter-tab");
  const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");
  const exportHistoryBtn = document.getElementById("exportHistoryBtn");
  const clearHistoryBtn = document.getElementById("clearHistoryBtn");
  const toastContainer = document.getElementById("toastContainer");

  let selectedRating = null;
  let allHistoryReviews = [];
  let currentFilter = "all";
  let lastAnalysisData = null;

  // ==========================================
  // 1. Theme Management (Dark / Light Mode)
  // ==========================================
  function initTheme() {
    const savedTheme = localStorage.getItem("fake-review-theme");
    const systemPrefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = savedTheme || (systemPrefersDark ? "dark" : "light");
    setTheme(initialTheme);
  }

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("fake-review-theme", theme);
    if (theme === "dark") {
      themeIcon.textContent = "☀️";
      themeText.textContent = "Light Mode";
    } else {
      themeIcon.textContent = "🌙";
      themeText.textContent = "Dark Mode";
    }
  }

  themeToggleBtn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    setTheme(current === "dark" ? "light" : "dark");
  });

  // ==========================================
  // 2. Star Rating Component
  // ==========================================
  function updateStarDisplay(rating) {
    starBtns.forEach((btn) => {
      const val = parseInt(btn.getAttribute("data-value"), 10);
      if (rating && val <= rating) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    if (rating) {
      starRatingLabel.textContent = STAR_LABELS[rating] || `${rating} Stars`;
      clearRatingBtn.style.display = "inline";
    } else {
      starRatingLabel.textContent = "No rating";
      clearRatingBtn.style.display = "none";
    }
  }

  starBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const val = parseInt(btn.getAttribute("data-value"), 10);
      if (selectedRating === val) {
        selectedRating = null;
      } else {
        selectedRating = val;
      }
      updateStarDisplay(selectedRating);
    });

    btn.addEventListener("mouseenter", () => {
      const val = parseInt(btn.getAttribute("data-value"), 10);
      starBtns.forEach((b) => {
        const bv = parseInt(b.getAttribute("data-value"), 10);
        if (bv <= val) b.classList.add("hover");
        else b.classList.remove("hover");
      });
      starRatingLabel.textContent = STAR_LABELS[val] || `${val} Stars`;
    });
  });

  document.getElementById("starRatingContainer").addEventListener("mouseleave", () => {
    starBtns.forEach((b) => b.classList.remove("hover"));
    updateStarDisplay(selectedRating);
  });

  clearRatingBtn.addEventListener("click", () => {
    selectedRating = null;
    updateStarDisplay(null);
  });

  // ==========================================
  // 3. Textarea Live Character & Word Counter
  // ==========================================
  function updateCounters() {
    const text = reviewInput.value;
    charCountEl.textContent = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).filter(Boolean).length : 0;
    wordCountEl.textContent = words;

    // Estimate reading time (~200 words per minute)
    const seconds = Math.max(1, Math.round((words / 200) * 60));
    readingTimeEl.textContent = words > 0 ? `⏱️ ~${seconds}s read` : "⏱️ ~0s read";
  }

  reviewInput.addEventListener("input", updateCounters);

  // Paste Tool
  pasteBtn.addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        reviewInput.value = text;
        updateCounters();
        showToast("Text pasted from clipboard", "success");
      }
    } catch (err) {
      showToast("Unable to read clipboard. Please paste manually (Ctrl+V).", "error");
    }
  });

  // Clear Text Tool
  clearTextBtn.addEventListener("click", () => {
    reviewInput.value = "";
    updateCounters();
  });

  // ==========================================
  // 4. Sample Review Presets
  // ==========================================
  document.querySelectorAll(".sample-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const sampleKey = chip.getAttribute("data-sample");
      const sample = SAMPLES[sampleKey];
      if (sample) {
        reviewInput.value = sample.review;
        selectedRating = sample.rating;
        updateStarDisplay(selectedRating);
        updateCounters();
        showToast(`Loaded sample preset!`, "success");
      }
    });
  });

  // Reset all
  resetBtn.addEventListener("click", () => {
    reviewInput.value = "";
    selectedRating = null;
    updateStarDisplay(null);
    updateCounters();
    resultsSection.classList.remove("visible");
  });

  // Copy Summary Report
  copyReportBtn.addEventListener("click", () => {
    if (!lastAnalysisData) return;
    const report = `Fake Review Trap Report
Verdict: ${lastAnalysisData.verdict}
Risk Score: ${lastAnalysisData.score}/100
Review: "${lastAnalysisData.review || reviewInput.value.trim()}"
Signals:
${lastAnalysisData.reasons.map((r) => ` - ${r}`).join("\n")}`;

    navigator.clipboard.writeText(report).then(() => {
      showToast("Audit report copied to clipboard!", "success");
    }).catch(() => {
      showToast("Failed to copy report", "error");
    });
  });

  // ==========================================
  // 5. Toast Notifications
  // ==========================================
  function showToast(message, type = "error") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "success" ? "✅" : "⚠️";
    toast.innerHTML = `<span style="font-size: 1.15rem;">${icon}</span> <span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  }

  // ==========================================
  // 6. Form Submission & Analysis
  // ==========================================
  analyzeForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const reviewText = reviewInput.value.trim();
    if (!reviewText) {
      showToast("Please enter or paste a review to analyze.");
      reviewInput.focus();
      return;
    }

    setLoading(true);

    try {
      const payload = {
        review: reviewText,
        rating: selectedRating !== null ? selectedRating : undefined
      };

      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMsg = data.message || data.error || "Analysis failed.";
        showToast(errorMsg, "error");
        return;
      }

      lastAnalysisData = { ...data, review: reviewText };
      displayResults(data);
      showToast("Review analysis completed successfully!", "success");
      loadHistory();
    } catch (err) {
      console.error("API error:", err);
      showToast("Could not connect to Fake Review Trap server. Ensure the backend is running at http://127.0.0.1:5000.", "error");
    } finally {
      setLoading(false);
    }
  });

  function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    if (isLoading) {
      btnText.textContent = "Running Deep Authenticity Audit...";
      btnSpinner.style.display = "inline-block";
    } else {
      btnText.textContent = "Analyze Review Authenticity";
      btnSpinner.style.display = "none";
    }
  }

  // ==========================================
  // 7. Results Rendering & Speedometer Gauge
  // ==========================================
  function displayResults(data) {
    const verdict = data.verdict || "Suspicious";
    const score = typeof data.score === "number" ? data.score : 0;
    const reasons = Array.isArray(data.reasons) ? data.reasons : [];
    const details = data.details || {};

    // 1. Radial Speedometer Gauge Calculation
    // Circle radius = 90 => circumference = 2 * PI * 90 ≈ 565.48
    const circumference = 565.48;
    const offset = circumference - (Math.min(100, Math.max(0, score)) / 100) * circumference;

    gaugeFill.className = "gauge-fill";
    if (verdict === "Genuine") {
      gaugeFill.classList.add("gauge-genuine");
      gaugeRiskTag.textContent = "GENUINE / LOW RISK";
      gaugeRiskTag.style.color = "var(--genuine-color)";
    } else if (verdict === "Suspicious") {
      gaugeFill.classList.add("gauge-suspicious");
      gaugeRiskTag.textContent = "SUSPICIOUS PATTERNS";
      gaugeRiskTag.style.color = "var(--suspicious-color)";
    } else {
      gaugeFill.classList.add("gauge-fake");
      gaugeRiskTag.textContent = "FABRICATED / HIGH RISK";
      gaugeRiskTag.style.color = "var(--fake-color)";
    }

    // Animate score counter
    animateNumber(gaugeScore, 0, score, 800);
    setTimeout(() => {
      gaugeFill.style.strokeDashoffset = offset;
    }, 50);

    // 2. Verdict Badge
    verdictBadge.className = "verdict-badge";
    if (verdict === "Genuine") {
      verdictBadge.classList.add("badge-genuine");
      verdictIcon.textContent = "🛡️";
      verdictText.textContent = "Genuine Product Review";
      verdictSummary.textContent = "The review displays organic syntactic variation, grounded physical features, and balanced sentiment consistent with authentic consumer usage.";
    } else if (verdict === "Suspicious") {
      verdictBadge.classList.add("badge-suspicious");
      verdictIcon.textContent = "⚠️";
      verdictText.textContent = "Suspicious Review Detected";
      verdictSummary.textContent = "The review exhibits abnormal patterns such as rating-sentiment conflicts, unnatural repetition, or superficial praise with low contextual depth.";
    } else {
      verdictBadge.classList.add("badge-fake");
      verdictIcon.textContent = "🚨";
      verdictText.textContent = "Fabricated / Fake Review";
      verdictSummary.textContent = "High-confidence detection of fabricated review activity: aggressive promotional wording, hyperbolic clichés, extreme formatting, or commercial spam links.";
    }

    // 3. Linear Meter
    meterFill.className = "meter-fill";
    if (verdict === "Genuine") meterFill.classList.add("meter-genuine");
    else if (verdict === "Suspicious") meterFill.classList.add("meter-suspicious");
    else meterFill.classList.add("meter-fake");

    meterFill.style.width = "0%";
    setTimeout(() => {
      meterFill.style.width = `${Math.min(100, Math.max(3, score))}%`;
    }, 100);

    // 4. Category Breakdown Bars
    updateCategoryBreakdowns(reasons, details);

    // 5. Reasons List
    reasonsList.innerHTML = "";
    if (reasons.length === 0) {
      const li = document.createElement("li");
      li.className = "reason-item item-genuine";
      li.innerHTML = `<span class="reason-icon">✅</span><span>No suspicious patterns or flags detected. Tone appears organic and balanced.</span>`;
      reasonsList.appendChild(li);
    } else {
      reasons.forEach((reason) => {
        const li = document.createElement("li");
        const isOrganic = reason.toLowerCase().includes("authentic") || reason.toLowerCase().includes("organic") || reason.toLowerCase().includes("natural");
        const isFake = verdict === "Fake" && !isOrganic;

        if (isOrganic) {
          li.className = "reason-item item-genuine";
          li.innerHTML = `<span class="reason-icon">✅</span><span>${escapeHtml(reason)}</span>`;
        } else if (isFake) {
          li.className = "reason-item item-fake";
          li.innerHTML = `<span class="reason-icon">🚨</span><span>${escapeHtml(reason)}</span>`;
        } else {
          li.className = "reason-item item-suspicious";
          li.innerHTML = `<span class="reason-icon">⚠️</span><span>${escapeHtml(reason)}</span>`;
        }
        reasonsList.appendChild(li);
      });
    }

    // 6. Diagnostic Metrics Grid
    metricWords.textContent = details.word_count !== undefined ? details.word_count : "-";
    metricCaps.textContent = details.caps_percentage !== undefined ? `${details.caps_percentage}%` : "-";
    metricExclamations.textContent = details.exclamation_count !== undefined ? details.exclamation_count : "-";
    metricPolarity.textContent = details.sentiment_polarity !== undefined ? (details.sentiment_polarity > 0 ? `+${details.sentiment_polarity}` : `${details.sentiment_polarity}`) : "0.0";
    metricDiversity.textContent = details.lexical_diversity !== undefined ? `${Math.round(details.lexical_diversity * 100)}%` : "-";
    if (metricEngine) {
      metricEngine.textContent = details.ml_active ? "Rules + ML" : "Rule Engine";
    }

    // Reveal results section
    resultsSection.classList.add("visible");
    resultsSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function updateCategoryBreakdowns(reasons, details) {
    const reasonsStr = reasons.join(" ").toLowerCase();

    // 1. Caps & Punctuation
    const capsPct = details.caps_percentage || 0;
    const exclCount = details.exclamation_count || 0;
    let capsScore = Math.min(100, Math.round((capsPct * 1.5) + (exclCount * 12)));
    barScoreCaps.textContent = `${capsScore}%`;
    miniBarCaps.style.width = `${capsScore}%`;
    miniBarCaps.className = `mini-bar-fill ${getMeterClass(capsScore)}`;

    // 2. Hype & Clichés
    let hypeScore = reasonsStr.includes("cliché") || reasonsStr.includes("hype") ? 85 : (reasonsStr.includes("generic") ? 50 : 5);
    barScoreHype.textContent = `${hypeScore}%`;
    miniBarHype.style.width = `${hypeScore}%`;
    miniBarHype.className = `mini-bar-fill ${getMeterClass(hypeScore)}`;

    // 3. Repetition & Quality
    let repScore = reasonsStr.includes("repeated") || reasonsStr.includes("repetitive") ? 90 : (details.lexical_diversity < 0.6 ? 55 : 5);
    barScoreRepetition.textContent = `${repScore}%`;
    miniBarRepetition.style.width = `${repScore}%`;
    miniBarRepetition.className = `mini-bar-fill ${getMeterClass(repScore)}`;

    // 4. Promotional Spam
    let promoScore = reasonsStr.includes("promotional") || reasonsStr.includes("link") || reasonsStr.includes("voucher") ? 95 : 0;
    barScorePromo.textContent = `${promoScore}%`;
    miniBarPromo.style.width = `${promoScore}%`;
    miniBarPromo.className = `mini-bar-fill ${getMeterClass(promoScore)}`;

    // 5. Rating Consistency
    let ratingScore = details.rating_conflict ? 90 : 0;
    barScoreRating.textContent = details.rating_conflict ? "Conflict" : "Aligned";
    miniBarRating.style.width = details.rating_conflict ? "90%" : "5%";
    miniBarRating.className = `mini-bar-fill ${details.rating_conflict ? "meter-fake" : "meter-genuine"}`;
  }

  function getMeterClass(score) {
    if (score >= 65) return "meter-fake";
    if (score >= 35) return "meter-suspicious";
    return "meter-genuine";
  }

  function animateNumber(element, start, end, duration) {
    let startTime = null;
    function animation(currentTime) {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      element.textContent = Math.floor(progress * (end - start) + start);
      if (progress < 1) {
        requestAnimationFrame(animation);
      } else {
        element.textContent = end;
      }
    }
    requestAnimationFrame(animation);
  }

  // ==========================================
  // 8. History Management, Filter Tabs & Search
  // ==========================================
  async function loadHistory() {
    try {
      const res = await fetch(`${API_BASE}/api/history?limit=30`);
      if (!res.ok) throw new Error("Failed to fetch history");

      const data = await res.json();
      allHistoryReviews = data.reviews || [];
      renderHistory();
    } catch (err) {
      console.warn("Could not load history:", err);
      historyList.innerHTML = `<div class="empty-history">Backend not connected. History will display once the backend server is reachable at http://127.0.0.1:5000.</div>`;
    }
  }

  function renderHistory() {
    const query = historySearchInput.value.toLowerCase().trim();

    // Filter by category tab and search query
    const filtered = allHistoryReviews.filter((item) => {
      const matchesCategory = currentFilter === "all" || item.verdict.toLowerCase() === currentFilter.toLowerCase();
      const matchesSearch = !query || item.review.toLowerCase().includes(query) || (item.verdict && item.verdict.toLowerCase().includes(query));
      return matchesCategory && matchesSearch;
    });

    historyCountBadge.textContent = `${filtered.length} of ${allHistoryReviews.length} saved`;

    if (filtered.length === 0) {
      historyList.innerHTML = `<div class="empty-history">No reviews matching the current filter. Test a preset or analyze a review!</div>`;
      return;
    }

    historyList.innerHTML = "";
    filtered.forEach((item) => {
      const card = document.createElement("div");
      card.className = "history-card";

      const starsDisplay = item.rating ? "★".repeat(item.rating) + "☆".repeat(5 - item.rating) : "No rating";
      const dateFormatted = formatTimestamp(item.created_at);

      let pillClass = "pill-suspicious";
      if (item.verdict === "Genuine") pillClass = "pill-genuine";
      if (item.verdict === "Fake") pillClass = "pill-fake";

      card.innerHTML = `
        <div class="history-card-top">
          <span class="history-pill ${pillClass}">${item.verdict} (${item.score}%)</span>
          <span style="color: #f59e0b; font-size: 0.9rem; font-weight: 600;">${starsDisplay}</span>
        </div>
        <div class="history-text" title="${escapeHtml(item.review)}">${escapeHtml(item.review)}</div>
        <div class="history-meta">
          <span>${item.reasons.length} flag(s) &bull; <small style="text-decoration: underline; color: var(--primary);">Click to inspect</small></span>
          <span>${dateFormatted}</span>
        </div>
      `;

      card.addEventListener("click", () => {
        reviewInput.value = item.review;
        selectedRating = item.rating;
        updateStarDisplay(selectedRating);
        updateCounters();
        lastAnalysisData = item;
        displayResults(item);
        showToast(`Loaded review #${item.id} from history`, "success");
      });

      historyList.appendChild(card);
    });
  }

  // Filter Tabs
  filterTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      filterTabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      currentFilter = tab.getAttribute("data-filter");
      renderHistory();
    });
  });

  // History Search
  historySearchInput.addEventListener("input", renderHistory);

  refreshHistoryBtn.addEventListener("click", () => {
    loadHistory();
    showToast("History refreshed", "success");
  });

  exportHistoryBtn.addEventListener("click", () => {
    window.open(`${API_BASE}/api/history/export`, "_blank");
    showToast("Exporting review history to CSV...", "success");
  });

  clearHistoryBtn.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to clear all analyzed review history from SQLite?")) {
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/api/history`, { method: "DELETE" });
      const data = await res.json();
      if (res.ok) {
        showToast(data.message || "History cleared", "success");
        loadHistory();
      } else {
        showToast(data.error || "Failed to clear history", "error");
      }
    } catch (err) {
      showToast("Cannot connect to server to clear history", "error");
    }
  });

  // Helpers
  function formatTimestamp(isoStr) {
    if (!isoStr) return "";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    } catch (e) {
      return isoStr;
    }
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Initialize
  initTheme();
  updateCounters();
  loadHistory();
});
