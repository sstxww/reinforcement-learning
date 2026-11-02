"""V7 regression: a branch-ref lease is not a global merge mutex."""
import importlib.util
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'scripts' / 'v7_merge_safety_0a1a530f32.py'
spec = importlib.util.spec_from_file_location('gate', P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
A = 'a' * 40
B = 'b' * 40
C = 'c' * 40


def state(*, before=A, after=A, head=B, protected=True, base='main', draft=False,
          mergeable=True, clean=True, ci=True, enforced=True):
    return mod.evaluate(
        main_before={'commit': {'sha': before}, 'protected': protected},
        main_after={'commit': {'sha': after}, 'protected': protected},
        pr={'number': 175, 'base': {'ref': base}, 'head': {'sha': head},
            'draft': draft, 'state': 'open', 'mergeable': mergeable,
            'mergeable_state': 'clean' if clean else 'dirty'},
        expected_main=A, expected_head=B, exact_head_ci_success=ci,
        enforcement_verified=enforced)


def test_green_structural_snapshot_still_never_authorizes_a_merge():
    result = state()
    assert result['review_candidate'] is True
    assert result['merge_authorized'] is False


def test_lease_does_not_make_unprotected_main_exclusive():
    result = state(protected=False, enforced=False)
    assert 'main_branch_unprotected' in result['blockers']
    assert 'globally_enforced_single_merge_entry_unproven' in result['blockers']
    assert result['merge_authorized'] is False


def test_concurrent_main_merge_invalidates_snapshot():
    result = state(after=C)
    assert 'main_head_drift_or_expected_mismatch' in result['blockers']
    assert not result['review_candidate']


def test_stale_pr_head_and_stacked_base_block():
    result = state(head=C, base='agent/learning/v1')
    assert 'pr_head_drift' in result['blockers']
    assert 'stacked_or_wrong_target' in result['blockers']


def test_draft_unknown_mergeability_and_old_ci_block():
    result = state(draft=True, mergeable=None, clean=False, ci=False)
    assert {'draft_pr','mergeability_not_clean','latest_head_ci_not_verified'} <= set(result['blockers'])


def test_no_external_enforcement_proof_never_counts_as_exclusive():
    result = state(enforced=False)
    assert result['review_candidate']
    assert not result['merge_authorized']
    assert 'globally_enforced_single_merge_entry_unproven' in result['blockers']


def test_snapshot_requires_full_sha_before_network():
    try:
        mod.snapshot(175, 'bad', B)
    except ValueError:
        pass
    else:
        raise AssertionError('short SHA accepted')
