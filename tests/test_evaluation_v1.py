from tavern_ai.evaluate import evaluate
import pytest

def test_nonpositive_count_fails_fast():
    with pytest.raises(ValueError,match="games"):
        evaluate("baseline",None,0,1)

def test_missing_model_fails_fast():
    with pytest.raises(FileNotFoundError,match="checkpoint"):
        evaluate("model",None,1,1)

def test_unknown_policy_fails_fast():
    with pytest.raises(ValueError,match="policy"):
        evaluate("unknown",None,1,1)
