"""The shared text preparation every service uses (provided; level 0).

prep(text) = tokenizer(normalizer(text)). Replacing the normaliser or the
tokenizer therefore changes the scores of every service at once.
"""
from sanad import data, registry

LEVEL = 0


class Pipeline:
    def __init__(self, parts=None):
        self.parts = dict(registry.config(), **(parts or {}))
        self.normalize = registry.load("normalize", self.parts["normalize"]).normalize
        tok = registry.load("tokenize", self.parts["tokenize"])
        self.tokenizer = tok.Tokenizer()
        # A fitted tokenizer learns from the training tickets only.
        self.tokenizer.fit([self.normalize(t["text"]) for t in data.tickets("train")])

    def prep(self, text):
        return self.tokenizer.tokenize(self.normalize(text))

    def router(self, version=None):
        mod = registry.load("router", version or self.parts["router"])
        r = mod.Router(self.prep)
        r.fit(data.tickets("train"))
        return r

    def search(self, version=None):
        mod = registry.load("search", version or self.parts["search"])
        s = mod.Search(self.prep, data.faq())
        s.fit()
        return s

    def keyboard(self, version=None):
        mod = registry.load("keyboard", version or self.parts["keyboard"])
        k = mod.Keyboard(self.prep)
        k.fit(data.tickets("train"))
        return k
