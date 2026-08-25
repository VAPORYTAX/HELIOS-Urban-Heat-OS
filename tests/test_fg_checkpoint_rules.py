from app.fortyguard_live.checkpoint_history import TERMINAL
def test_no_data_is_terminal():
    assert "COMPLETE_NO_DATA" in TERMINAL
def test_with_data_is_terminal():
    assert "COMPLETE_WITH_DATA" in TERMINAL
