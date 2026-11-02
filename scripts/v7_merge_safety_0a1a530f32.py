"""V7 read-only main-merge safety snapshot; NEVER acquires or grants a merge lease.

Why fail-closed? A coordination ref was acquired during PR #164, while a
concurrent writer merged the same PR. Ref ownership is not global exclusion.
See https://github.com/sstxww/reinforcement-learning/issues/182.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPO = 'sstxww/reinforcement-learning'
API = f'https://api.github.com/repos/{REPO}'
HEX40 = re.compile(r'[0-9a-f]{40}\\Z')


def get_json(path: str) -> dict:
    if not path.startswith('/') or '://' in path or '..' in path:
        raise ValueError('Only fixed repository-relative GitHub API paths are allowed')
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    headers = {'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28',
               'User-Agent': 'autotavern-v7-fail-closed-merge-snapshot'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        with urlopen(Request(API + path, headers=headers), timeout=20) as response:
            result = json.load(response)
            if not isinstance(result, dict):
                raise ValueError('Unexpected GitHub response')
            return result
    except HTTPError as error:
        raise RuntimeError(f'GitHub API unavailable: HTTP {error.code} for {path}') from error


def evaluate(*, main_before: dict, main_after: dict, pr: dict,
             expected_main: str, expected_head: str,
             exact_head_ci_success: bool, enforcement_verified: bool) -> dict:
    """Produce an audit, never a merge authorization; enforcement is external.

    Even if a caller says enforcement_verified=True, an *independent* server-
    enforced queue/bypass review must be completed by an actual integrator.
    """
    problems = []
    before = main_before.get('commit', {}).get('sha')
    after = main_after.get('commit', {}).get('sha')
    if before != expected_main or after != expected_main:
        problems.append('main_head_drift_or_expected_mismatch')
    if not main_after.get('protected'):
        problems.append('main_branch_unprotected')
    if pr.get('base', {}).get('ref') != 'main':
        problems.append('stacked_or_wrong_target')
    if pr.get('head', {}).get('sha') != expected_head:
        problems.append('pr_head_drift')
    if pr.get('draft'):
        problems.append('draft_pr')
    if pr.get('state') != 'open':
        problems.append('pr_not_open')
    if pr.get('mergeable') is not True or pr.get('mergeable_state') != 'clean':
        problems.append('mergeability_not_clean')
    if not exact_head_ci_success:
        problems.append('latest_head_ci_not_verified')
    if not enforcement_verified:
        problems.append('globally_enforced_single_merge_entry_unproven')
    if not HEX40.fullmatch(expected_main) or not HEX40.fullmatch(expected_head):
        problems.append('invalid_expected_sha')
    return {'schema': 1, 'repository': REPO,
            'observed_main_before': before, 'observed_main_after': after,
            'expected_main': expected_main, 'expected_pr_head': expected_head,
            'pr_number': pr.get('number'),
            'review_candidate': not any(x for x in problems if x != 'globally_enforced_single_merge_entry_unproven'),
            'merge_authorized': False,  # Not a mutex/merge executor.
            'blockers': problems,
            'warning': 'A CAS ref alone does not exclude other sessions; never merge from this report.'}


def snapshot(number: int, expected_main: str, expected_head: str) -> dict:
    if number < 1 or not HEX40.fullmatch(expected_main) or not HEX40.fullmatch(expected_head):
        raise ValueError('Required: PR number and full 40-character expected SHAs')
    main_before = get_json('/branches/main')
    pr = get_json(f'/pulls/{number}')
    # We deliberately never infer CI success from a green icon or a prior head.
    main_after = get_json('/branches/main')
    report = evaluate(main_before=main_before, main_after=main_after, pr=pr,
                      expected_main=expected_main, expected_head=expected_head,
                      exact_head_ci_success=False, enforcement_verified=False)
    report['check_note'] = ('Read-only structural preflight. Exact latest-head and '
                            'merged-code CI, reviews, branch rules and exclusive '
                            'entry must be independently proven before merge.')
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pr', type=int, required=True)
    p.add_argument('--expected-main', required=True)
    p.add_argument('--expected-head', required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    report = snapshot(args.pr, args.expected_main, args.expected_head)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\\n')
    print(json.dumps(report))
    # Nonzero: a read-only report NEVER means authorized to merge.
    raise SystemExit(2 if report['blockers'] else 0)


if __name__ == '__main__':
    main()
