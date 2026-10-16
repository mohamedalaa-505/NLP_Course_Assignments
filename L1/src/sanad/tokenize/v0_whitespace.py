"""Tokenizer v0: split on whitespace (provided; level 0).

Punctuation stays attached: "portal," and "portal" are different tokens.
Level 3 replaces this part and measures what that costs every service.
"""
LEVEL = 0


class Tokenizer:
    def fit(self, texts):
        """Nothing to learn."""
        return self

    def tokenize(self, text):
        return text.split()
