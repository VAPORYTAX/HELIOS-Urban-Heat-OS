def choose_thinking(task_type: str, mode: str, force: bool | None = None) -> bool:
    if force is not None:
        return force
    if mode == 'operational':
        return False
    if task_type in {'situation_assessment','intervention_planning','portfolio_optimization','evidence_review','executive_brief'}:
        return False
    if task_type == 'scenario_comparison':
        return True
    return False

def choose_model(task_type: str, config: dict) -> str:
    if task_type in {'situation_assessment'}:
        return config['fallback_model']
    return config['model']


def choose_profile(task_type: str, mode: str, force_thinking: bool | None = None) -> dict:
    thinking = choose_thinking(task_type, mode, force_thinking)
    if thinking:
        return {
            "name": "deep",
            "thinking": True,
            "token_budget": 16000,
            "include_raw_evidence": True,
            "max_tokens": 3600,
            "temperature": 0.4,
            "timeout_seconds": 300.0,
        }
    return {
        "name": "fast",
        "thinking": False,
        "token_budget": 7000,
        "include_raw_evidence": False,
        "max_tokens": 2400,
        "temperature": 0.2,
        "timeout_seconds": 210.0,
    }
