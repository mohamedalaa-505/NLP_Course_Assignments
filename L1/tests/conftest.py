import os
from pathlib import Path

import pytest

os.environ.setdefault("SANAD_DATA", str(Path(__file__).resolve().parent.parent / "data"))

V0 = {"normalize": "v0_identity", "tokenize": "v0_whitespace"}


@pytest.fixture
def pipeline_v0():
    from sanad.pipeline import Pipeline
    return Pipeline(V0)


@pytest.fixture
def pipeline_v1():
    from sanad.pipeline import Pipeline
    return Pipeline(dict(V0, normalize="v1_policies"))


# Levels 3-6 compare versions under the reference shared parts of the level before.
V3 = {"normalize": "v2_nfc", "tokenize": "v1_policy"}


@pytest.fixture
def pipeline():
    """pipeline(**parts): a Pipeline over V3 with some parts changed."""
    from sanad.pipeline import Pipeline
    return lambda **parts: Pipeline(dict(V3, **parts))
