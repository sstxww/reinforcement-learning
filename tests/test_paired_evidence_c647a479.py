import pytest
from tavern_ai.paired_evidence import paired_report


def receipt(seed, rank, *, policy='model', guard=0, seat=0):
    spots=list(range(1, 9))
    spots[seat],spots[rank-1]=spots[rank-1],spots[seat]
    return {'environment':'TavernGym','completed':True,'agent_id':'test',
            'engine_version':'1.1.0','engine_source_hash':'6d8712c93022ba11',
            'seed':seed,'controlled_seat':seat,'placements':spots,
            'turns':15,'decisions':50,'policy':policy,
            'model_sha256':('a'*64 if policy!='baseline' else None),
            'guard_interventions':guard,'truncated_combats':0,'turn_limit_end':False}


def test_paired_report_zero_buys_cannot_establish_win():
    m=[receipt(1,8),receipt(2,8)]
    b=[receipt(2,6,policy='baseline'),receipt(1,7,policy='baseline')]
    r=paired_report(m,b)
    assert r['paired_seed_seat']==[{'seed':1,'seat':0},{'seed':2,'seat':0}]
    assert r['paired_rank_deltas']==[1,2]
    assert r['candidate_kind']=='raw_model'
    assert r['candidate']['top4_rate']==0
    assert r['candidate']['top4_wilson95'][1]>0
    assert r['checkpoint_bytes_verified_by_this_report'] is False


def test_guarded_model_is_explicit_and_not_mixed():
    c=receipt(1,8,guard=2)
    b=receipt(1,6,policy='baseline')
    assert paired_report([c],[b])['candidate_kind']=='guarded_model'
    with pytest.raises(ValueError,match='cannot mix'):
        paired_report([c,receipt(2,8)],[b,receipt(2,7,policy='baseline')])


@pytest.mark.parametrize('change,reason',[
    (lambda x:x.update(completed=False),'Incomplete'),
    (lambda x:x.update(placements=[8]*8),'permutation'),
    (lambda x:x.update(engine_source_hash='bad'),'engine mismatch'),
    (lambda x:x.update(truncated_combats=1),'Simulator guard'),
    (lambda x:x.update(model_sha256='bad'),'SHA256'),
    (lambda x:x.update(guard_interventions=-1),'invalid guard'),
    (lambda x:x.update(seed=True),'invalid seed'),
])
def test_reject_invalid_game(change,reason):
    c=receipt(1,8);change(c)
    with pytest.raises(ValueError,match=reason):
        paired_report([c],[receipt(1,7,policy='baseline')])


def test_reject_mismatched_seed_or_seat():
    with pytest.raises(ValueError,match='identical seed/seat'):
        paired_report([receipt(1,8)],[receipt(2,7,policy='baseline')])


def test_reject_duplicate_game_and_two_checkpoints():
    c=receipt(1,8);b=receipt(1,7,policy='baseline')
    with pytest.raises(ValueError,match='duplicate'):
        paired_report([c,c],[b,b])
    c2=receipt(2,8); c2['model_sha256']='b'*64
    with pytest.raises(ValueError,match='distinct model'):
        paired_report([c,c2],[b,receipt(2,7,policy='baseline')])


def test_controlled_seat_index_and_wilson_rate():
    c=receipt(13,2,seat=3);b=receipt(13,4,policy='baseline',seat=3)
    r=paired_report([c],[b]);assert r['paired_rank_deltas']==[-2]
    assert r['candidate']['top4_rate']==1
    assert r['candidate']['top4_wilson95'][0]<1


def test_guard_variant_even_without_interventions():
    c=receipt(1,8);c['policy_variant']='hero_cancel_guard_v1'
    assert paired_report([c],[receipt(1,8,policy='baseline')])['candidate_kind']=='guarded_model'
