from pathlib import Path
from app.intelligence.router import choose_thinking
s=Path(r'D:\HELIOS\scripts\activate_gemma4_live.py').read_text(encoding='utf-8-sig')
assert 'payload["force_thinking"] = False' in s
assert choose_thinking('portfolio_optimization','investment',False) is False
assert choose_thinking('portfolio_optimization','investment',None) is False
assert choose_thinking('scenario_comparison','planning',None) is True
print('PASS: force_thinking=False wired to activation')
print('PASS: portfolio optimization FAST')
print('PASS: scenario comparison DEEP')
