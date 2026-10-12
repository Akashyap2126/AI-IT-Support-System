import re


def predict_ticket(title, description):
    """
    AI-style ticket classification and priority prediction.

    Returns:
        category
        priority
        sentiment
        confidence
    """

    text = f"{title} {description}".lower()

    # -----------------------------
    # Category classification
    # -----------------------------

    category_keywords = {
        "network": [
            "wifi", "wi-fi", "internet", "network",
            "vpn", "connection", "connect", "ethernet"
        ],
        "hardware": [
            "laptop", "computer", "keyboard", "mouse",
            "monitor", "screen", "printer", "hard drive",
            "hardware"
        ],
        "software": [
            "software", "application", "app", "program",
            "crash", "error", "bug", "install", "update"
        ],
        "security": [
            "hack", "hacked", "phishing", "malware",
            "virus", "suspicious", "password", "breach",
            "unauthorized", "security"
        ],
        "account": [
            "account", "login", "log in", "password",
            "username", "access", "locked"
        ]
    }

    category_scores = {}

    for category, keywords in category_keywords.items():
        score = 0

        for keyword in keywords:
            if keyword in text:
                score += 1

        category_scores[category] = score

    predicted_category = max(
        category_scores,
        key=category_scores.get
    )

    highest_score = category_scores[predicted_category]

    if highest_score == 0:
        predicted_category = "general"
        confidence = 0.50
    else:
        confidence = min(
            0.60 + (highest_score * 0.08),
            0.95
        )

    # -----------------------------
    # Priority prediction
    # -----------------------------

    critical_keywords = [
        "breach",
        "hacked",
        "data loss",
        "ransomware",
        "malware",
        "server down",
        "critical"
    ]

    high_keywords = [
        "urgent",
        "unable to work",
        "production down",
        "security",
        "phishing",
        "virus",
        "blocked"
    ]

    low_keywords = [
        "minor",
        "question",
        "request",
        "suggestion",
        "slow"
    ]

    if any(keyword in text for keyword in critical_keywords):
        predicted_priority = "critical"

    elif any(keyword in text for keyword in high_keywords):
        predicted_priority = "high"

    elif any(keyword in text for keyword in low_keywords):
        predicted_priority = "low"

    else:
        predicted_priority = "medium"

    # -----------------------------
    # Sentiment analysis
    # -----------------------------

    negative_words = [
        "angry",
        "frustrated",
        "annoyed",
        "urgent",
        "terrible",
        "failed",
        "problem",
        "issue",
        "not working",
        "unable"
    ]

    positive_words = [
        "thanks",
        "thank you",
        "great",
        "working",
        "resolved"
    ]

    negative_score = sum(
        1 for word in negative_words if word in text
    )

    positive_score = sum(
        1 for word in positive_words if word in text
    )

    if negative_score > positive_score:
        sentiment = "negative"

    elif positive_score > negative_score:
        sentiment = "positive"

    else:
        sentiment = "neutral"

    return {
        "category": predicted_category,
        "priority": predicted_priority,
        "sentiment": sentiment,
        "confidence": round(confidence, 4),
        "model_version": "rule-based-ai-v1"
    }


def generate_response_suggestion(title, description, category, priority):
    """
    Generate an AI-style support response suggestion
    based on ticket information.
    """

    category = (category or "general").lower()
    priority = (priority or "medium").lower()

    if category == "network":
        response = (
            "We have received your network-related issue. "
            "Please restart your network connection and verify that "
            "your device is connected to the correct network. "
            "If the issue continues, our IT support team will investigate "
            "the connection further."
        )

    elif category == "security":
        response = (
            "Your security-related issue has been flagged for review. "
            "Please avoid clicking suspicious links or sharing your "
            "credentials. Our IT security team will investigate the "
            "reported activity and take the necessary action."
        )

    elif category == "hardware":
        response = (
            "We have received your hardware-related issue. "
            "Please check the device connections and restart the device "
            "if possible. If the problem continues, an IT support agent "
            "will inspect the hardware."
        )

    elif category == "software":
        response = (
            "We have received your software-related issue. "
            "Please restart the affected application and verify that "
            "you are using the latest available version. "
            "Our IT support team will investigate further if the issue persists."
        )

    elif category == "account":
        response = (
            "We have received your account-related issue. "
            "Please verify your login details and try signing in again. "
            "If you remain unable to access your account, our support team "
            "will assist you with account recovery."
        )

    else:
        response = (
            "We have received your support request. "
            "Our IT support team will review the reported issue "
            "and provide further assistance."
        )

    if priority == "critical":
        response = (
            "This ticket has been identified as critical and will be "
            "prioritized by the IT support team. "
            + response
        )

    elif priority == "high":
        response = (
            "This issue has been marked as high priority. "
            + response
        )

    return response