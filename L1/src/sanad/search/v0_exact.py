"""Search v0: rank passages by exact token overlap with the question (Level 1)."""
from sanad.data import passage_text

LEVEL = 1
STUDENT = ("Search.fit", "Search.score", "Search.search")


class Search:
    def __init__(self, prep, passages):
        self.prep = prep
        self.passages = passages
        self.tokens = {}

    def fit(self):
        """Prepare each passage once: id -> set of its tokens."""
        raise NotImplementedError("Level 1: fit")

    def score(self, query_tokens, pid):
        """Number of distinct query tokens that occur in passage pid."""
        raise NotImplementedError("Level 1: score")

    def search(self, query, k=3):
        """Ids of the k best passages with a positive score; ties by id."""
        raise NotImplementedError("Level 1: search")
