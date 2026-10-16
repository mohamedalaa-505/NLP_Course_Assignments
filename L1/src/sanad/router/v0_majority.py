"""Router v0: always answer with the most frequent training intent (Level 1).

This is the baseline every later router must beat on the same split.
"""
from sanad.evaluate import majority_baseline

LEVEL = 1
STUDENT = ("Router.fit", "Router.predict")


class Router:
    def __init__(self, prep):
        self.prep = prep          # unused: the baseline never reads the text
        self.label = None

    def fit(self, tickets):
        """Remember the majority intent of the training tickets."""
        intents = [t["intent"] for t in tickets]
        self.label = majority_baseline(intents)

    def predict(self, text):
        """Return the remembered label, whatever the text says."""
        return self.label
