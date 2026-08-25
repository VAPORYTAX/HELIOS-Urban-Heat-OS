from app.intelligence.firewall import validate_answer

def packet():
    return {
        "state":{
            "cells":[{"cell_id":"c1","teu":100.0,"va_teu":120.0,"hazard_index":0.5,"exposure_index":0.4,"vulnerability_index":0.6,"confidence":0.8}],
            "optimizer":{"budget":100000.0,"total_cost":96000.0,"selected_count":2,"scenario":{"teu_reduction_pct":30.0,"teu_reduction":300.0,"va_teu_reduction":250.0,"thermal_roi":0.004,"confidence":0.75}},
            "quality":{"requires_human_review":True}
        },
        "evidence_refs":[{"ref":"e1"}]
    }

def valid():
    return {
        "decision_status":"review_required","headline":"x","summary":"y",
        "recommended_actions":[],"uncertainties":[],"evidence_refs":["e1"],
        "numeric_claims":{"optimizer.budget":100000.0},
        "requires_human_review":True
    }

def test_valid_answer_passes():
    a,v=validate_answer(valid(),packet())
    assert a is not None and v["valid"] is True

def test_numeric_hallucination_is_blocked():
    x=valid(); x["numeric_claims"]["optimizer.budget"]=200000
    _,v=validate_answer(x,packet())
    assert v["valid"] is False

def test_review_gate_cannot_be_bypassed():
    x=valid(); x["decision_status"]="recommend"; x["requires_human_review"]=False
    _,v=validate_answer(x,packet())
    assert v["valid"] is False
