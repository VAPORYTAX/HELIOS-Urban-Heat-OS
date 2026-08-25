from app.agents.engine import skeptic_agent, executive_agent

def test_skeptic_flags_fixture():
    out=skeptic_agent(
        optimizer={"confidence":0.8,"teu_reduction_pct":30},
        source_truth_categories={"fixture","derived"},
        mode="planning",
    )
    assert out["severity"]=="review"
    assert any("fixture" in x.lower() for x in out["content"]["issues"])

def test_operational_mode_blocks_fixture():
    out=skeptic_agent(
        optimizer={"confidence":0.9,"teu_reduction_pct":20},
        source_truth_categories={"fixture"},
        mode="operational",
    )
    assert out["severity"]=="block"

def test_executive_requires_review_if_skeptic_reviews():
    findings=[
        {"agent":"Planner","confidence":0.9,"content":{"actions":[]}},
        {"agent":"Evidence","confidence":0.9,"content":{}},
        {"agent":"Skeptic","confidence":0.95,"severity":"review","content":{}},
    ]
    out=executive_agent(findings,0.7)
    assert out["content"]["requires_human_review"] is True
    assert out["content"]["decision_status"]=="review_required"

def test_executive_can_recommend_when_clean():
    findings=[
        {"agent":"Planner","confidence":0.9,"content":{"actions":[{"x":1}]}},
        {"agent":"Evidence","confidence":0.9,"content":{}},
        {"agent":"Skeptic","confidence":0.95,"severity":"routine","content":{}},
    ]
    out=executive_agent(findings,0.7)
    assert out["content"]["decision_status"]=="recommend"
