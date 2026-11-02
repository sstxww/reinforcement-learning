from tavern_ai.evaluate import evaluate,summarize
import pytest

def test_nonpositive_count_fails_fast():
    with pytest.raises(ValueError,match="games"):
        evaluate(0,1)

def test_comparison_without_model_fails_fast():
    with pytest.raises(ValueError,match="requires a model"):
        evaluate(1,1,compare_baseline=True)

def test_summarize_placement_statistics():
    rows=[{"placements":[2,1,3,4,5,6,7,8],"seed":101},
          {"placements":[6,1,2,3,4,5,7,8],"seed":102}]
    result=summarize(rows)
    assert result["games"]==2
    assert result["mean_placement"]==4
    assert result["first_place_rate"]==0
    assert result["top4_rate"]==0.5
    assert result["seeds"]==[101,102]
