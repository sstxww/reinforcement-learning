"""Synthetic positive and negative tests, NOT genuine TavernGym games."""
import hashlib
import importlib.util
from pathlib import Path

import pytest

FILE = Path(__file__).resolve().parents[1] / 'scripts' / 'v7_seed_isolation_d2f99825.py'
spec = importlib.util.spec_from_file_location('seed_isolation_v7', FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SID = 's-20261103-d2f99825'


def fake_record(seed, agent, arm, model):
    return {'seed': seed, 'agent_id': agent, 'policy': arm, 'completed': True,
            'engine_source_hash': mod.ENGINE_HASH, 'turn_limit_end': False,
            'truncated_combats': 0, 'placements': list(range(1, 9)),
            'model_sha256': hashlib.sha256(Path(model).read_bytes()).hexdigest() if model else None}


def test_success_writes_every_seed_independently(tmp_path):
    s = mod.run_batch(session_id=SID, start_seed=99301, games=2, policy='baseline',
                      out_dir=tmp_path, game_fn=fake_record, validator=lambda row: True)
    assert s['status'] == 'complete'
    assert s['by_arm']['baseline']['placements_completed_only'] == [1, 1]
    assert (tmp_path / 'receipts/baseline-99302.json').is_file()


def test_one_model_failure_does_not_erase_other_games_or_fabricate_eighth(tmp_path):
    weights = tmp_path / 'checkpoint.zip'
    weights.write_bytes(b'synthetic-not-a-real-checkpoint')
    def runner(seed, agent, arm, model):
        if seed == 99302 and arm == 'model':
            raise RuntimeError('Full-game safety limit exceeded')
        return fake_record(seed, agent, arm, model)
    s = mod.run_batch(session_id=SID, start_seed=99301, games=2, policy='model',
                      compare_baseline=True, model=weights, out_dir=tmp_path,
                      game_fn=runner, validator=lambda row: True)
    assert s['status'] == 'failed_with_evidence'
    assert s['by_arm']['model']['completed'] == 1
    assert s['by_arm']['baseline']['completed'] == 2
    assert s['paired_complete_only']['seeds'] == [99301]
    failure = (tmp_path / 'failures/model-99302.json').read_text()
    assert 'Full-game safety limit exceeded' in failure
    assert 'no_placement_claimed' in failure
    assert '"placement"' not in failure
    assert (tmp_path / 'receipts/baseline-99302.json').exists()


def test_reject_model_hash_mismatch_without_writing_success(tmp_path):
    weights = tmp_path / 'model.zip'
    weights.write_bytes(b'fake')
    def wrong(*args):
        r = fake_record(*args)
        r['model_sha256'] = 'f' * 64
        return r
    s = mod.run_batch(session_id=SID, start_seed=99301, games=1,
                      policy='model', model=weights, out_dir=tmp_path,
                      game_fn=wrong, validator=lambda row: True)
    assert s['status'] == 'failed_with_evidence'
    assert not (tmp_path / 'receipts/model-99301.json').exists()


@pytest.mark.parametrize('kwargs', [
    {'session_id': 'invalid'}, {'games': 5}, {'policy': 'guarded'},
    {'compare_baseline': True}, {'start_seed': -1},
])
def test_preflight_fails_closed(tmp_path, kwargs):
    args = dict(session_id=SID, start_seed=99301, games=1, policy='baseline', out_dir=tmp_path)
    args.update(kwargs)
    with pytest.raises((ValueError, FileNotFoundError)):
        mod.run_batch(**args, game_fn=fake_record, validator=lambda row: True)
