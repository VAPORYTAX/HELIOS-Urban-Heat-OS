from app.contextforge.utility import context_utility,estimate_tokens,trim_ranked
def test_higher_confidence_improves_utility():
    assert context_utility(relevance=1,confidence=.9,spatial_match=1,freshness=1,decision_impact=1)>context_utility(relevance=1,confidence=.4,spatial_match=1,freshness=1,decision_impact=1)
def test_trim_respects_budget():
    kept,used=trim_ranked([{"utility_score":1.0,"payload":"a"*1000},{"utility_score":.5,"payload":"b"*1000}],400)
    assert used<=400 and len(kept)<=1
def test_estimate_tokens_positive(): assert estimate_tokens({"a":1})>0
