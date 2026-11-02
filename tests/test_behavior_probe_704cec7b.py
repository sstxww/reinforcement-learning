from tavern_ai.behavior_probe_704cec7b import action_category, summarize


def test_action_bands_and_end_turn():
    assert action_category(0) == "END_TURN"
    assert action_category(3) == "UPGRADE"
    assert action_category(8) == "BUY"
    assert action_category(15) == "BUY"
    assert action_category(46) == "PLAY"
    assert action_category(126) == "MAGNETIZE"


def test_legality_opportunity_separate_from_model_choices_and_guards():
    events = [
        {"turn": 2, "action": 0, "buy_legal": True, "forced_end": False,
         "public_observation_unchanged": None},
        {"turn": 3, "action": 8, "buy_legal": True, "forced_end": False,
         "public_observation_unchanged": False},
        {"turn": 3, "action": 21, "buy_legal": False, "forced_end": False,
         "public_observation_unchanged": True},
        {"turn": 3, "action": 21, "buy_legal": False, "forced_end": False,
         "public_observation_unchanged": True},
        {"turn": 3, "action": 0, "buy_legal": True, "forced_end": True,
         "public_observation_unchanged": None},
    ]
    d = summarize(events)
    assert d["selected_buys"] == 1
    assert d["buy_legal_decision_states"] == 3
    assert d["turns_with_any_legal_buy"] == 2
    assert d["end_turn_while_buy_legal"] == 2
    assert d["guard_forced_end_turns"] == 1
    assert d["model_actions"] == 4
    assert d["same_action_adjacent_within_turn"] == 1
    assert d["observable_unchanged_post_actions"] == 2
    assert d["per_turn"]["3"]["forced_ends"] == 1
    assert d["per_turn"]["3"]["model_ends"] == 0
