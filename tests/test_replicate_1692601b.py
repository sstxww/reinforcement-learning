from tavern_ai.replicate_1692601b import HELDOUT, LOCKED_ARM, paired_stats, summary

def test_prelocked_20_fresh_seeds():
    assert len(HELDOUT) == 20
    assert not (set(HELDOUT) & {49131, 49132, 59131, 59132, 59133, 59134})
    assert LOCKED_ARM == (7, "first")

def test_seat_specific_rank_not_own_zero_slot():
    fake = [{"controlled_seat": 3, "controlled_placement": 2,
             "placements": [8,7,6,2,5,4,3,1], "decisions": 5,
             "sales_interventions": 1, "unpaired_sales": 0},
            {"controlled_seat": 4, "controlled_placement": 6,
             "placements": [1,2,3,4,6,5,7,8], "decisions": 8,
             "sales_interventions": 0, "unpaired_sales": 0}]
    assert summary(fake)["ranks"] == [2, 6]
    assert summary(fake)["mean_rank"] == 4
    assert summary(fake)["sales"] == 1

def test_sign_test_ties_and_bootstrap():
    p = paired_stats([0,0,-1,-1,1])
    assert p["wins"] == 2 and p["losses"] == 1 and p["ties"] == 2
    assert p["exact_two_sided_nonzero_sign_p"] == 1.0
    assert p["bootstrap95_percentile"][0] <= p["mean_rank_delta"] <= p["bootstrap95_percentile"][1]
