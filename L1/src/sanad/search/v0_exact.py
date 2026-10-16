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
        for p in self.passages:
            self.tokens[p["id"]] = set(self.prep(passage_text(p)))

    def score(self, query_tokens, pid):
        """Number of distinct query tokens that occur in passage pid."""
        return len(set(query_tokens) & self.tokens[pid])

    def search(self, query, k=3):
        """Ids of the k best passages with a positive score; ties by id."""
        query_tokens = self.prep(query)
        scored = []
        for pid in self.tokens:
            s = self.score(query_tokens, pid)
            if s > 0:
                scored.append((s, pid))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [pid for s, pid in scored[:k]]
