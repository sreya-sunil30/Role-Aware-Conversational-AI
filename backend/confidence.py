# confidence.py

def calculate_confidence(reply: str, role: str) -> int:
    score = 0
    reply_lower = reply.lower()

    # Length-based confidence
    if len(reply) > 250:
        score += 40
    else:
        score += 20

    uncertain_words = ["maybe", "not sure", "might", "possibly", "i think"]
    if any(word in reply_lower for word in uncertain_words):
        score += 10
    else:
        score += 30

    # Base confidence
    score += 20

    # Role-based boost
    if role == "sap":
        sap_keywords = ["sap", "btp", "cloud foundry", "hana", "fiori"]
        if any(word in reply_lower for word in sap_keywords):
            score += 10

    if role == "coding":
        if "```" in reply or "function" in reply_lower or "class" in reply_lower:
            score += 10

    return min(score, 100)
