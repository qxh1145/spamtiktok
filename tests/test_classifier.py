import unittest
from src.classifier import Classifier

class TestClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = Classifier()

    def test_predict_spam(self):
        message = "Buy cheap meds now! Huge discount!"
        result = self.classifier.predict(message)
        self.assertTrue(result, "Expected message to be classified as spam")

    def test_predict_ham(self):
        message = "Hey, are we still meeting for lunch today?"
        result = self.classifier.predict(message)
        self.assertFalse(result, "Expected message to be classified as ham")

if __name__ == "__main__":
    unittest.main()
