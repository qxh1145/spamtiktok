class Classifier:
    def __init__(self):
        self.spam_keywords = ["buy", "cheap", "meds", "now", "discount", "cash", "winner", "prize", "free"]

    def predict(self, message: str) -> bool:
        """
        Predicts if a message is spam based on keywords.
        Returns True if spam, False if ham.
        """
        message_lower = message.lower()
        for keyword in self.spam_keywords:
            if keyword in message_lower:
                return True
        return False
