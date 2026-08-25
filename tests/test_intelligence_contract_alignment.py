from app.intelligence.firewall import collect_authoritative_numbers, ALLOWED_ACTION_KEYS

def test_provider_native_optimizer_numbers():
    packet={"state":{"optimizer":{
        "budget":100000.0,
        "total_cost":99000.0,
        "teu_reduction":113.7,
        "va_teu_reduction":112.3,
        "confidence":0.71
    },"quality":{"health_score":0.94}}}
    nums=collect_authoritative_numbers(packet)
    assert nums["optimizer.budget"]==100000.0
    assert nums["optimizer.total_cost"]==99000.0
    assert nums["optimizer.teu_reduction"]==113.7
    assert nums["optimizer.va_teu_reduction"]==112.3
    assert nums["optimizer.confidence"]==0.71
    assert nums["quality.health_score"]==0.94

def test_action_contract_expected_keys():
    assert "reason" in ALLOWED_ACTION_KEYS
    assert "action" not in ALLOWED_ACTION_KEYS
    assert "rationale" not in ALLOWED_ACTION_KEYS
