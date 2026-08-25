from app.quality.metrics import va_teu, validate_metric_relationships

def test_va_teu_can_exceed_total_teu_semantically():
    assert va_teu(1.0, 100, 0.8) == 180.0

def test_metric_invariants_accept_valid_values():
    issues = validate_metric_relationships(
        teu=100, va_teu_value=150,
        population=1000, vulnerable_population=300,
        vulnerability_index=0.5,
    )
    assert issues == []

def test_metric_invariants_reject_bad_vulnerability():
    issues = validate_metric_relationships(
        teu=100, va_teu_value=100,
        population=1000, vulnerable_population=300,
        vulnerability_index=1.5,
    )
    assert issues
