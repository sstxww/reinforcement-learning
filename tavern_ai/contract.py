"""Pinned TavernArena/TavernGym 1.1.0 contract; fail closed on changes."""
from __future__ import annotations
UPSTREAM_COMMIT = "fb61201a557ddd36a411cf44aac51ce4d9b606ce"
PATCH_SHA256 = "1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0"
ENGINE_HASH = "6d8712c93022ba11"
CATALOG_SHA256 = "c4c42e6ce5060e1b79fbcd5f4edbf6d17495f0f52690072481d690610f7ef6d7"
RULESET_ID = "tg36-bc45cfc55a0e5cd6c14c"
FEATURES, CARDS, ACTIONS = 4017, 447, 245

def verify_engine():
    import taverngym
    values = {
        "version": taverngym.version(),
        "source_hash": taverngym.build_info()["source_hash"],
        "features": getattr(taverngym, "OBS2_FLOATS", None),
        "cards": getattr(taverngym, "OBS2_CARDS", None),
        "actions": taverngym.N_ACTIONS,
        "n_cards": taverngym.N_CARDS,
    }
    if (values["version"],values["source_hash"],values["features"],values["cards"],values["actions"]) != ("1.1.0",ENGINE_HASH,FEATURES,CARDS,ACTIONS):
        raise RuntimeError(f"Unsupported TavernGym engine/observation: {values}")
    return values

if __name__ == "__main__":
    import json
    print(json.dumps(verify_engine(), indent=2))
