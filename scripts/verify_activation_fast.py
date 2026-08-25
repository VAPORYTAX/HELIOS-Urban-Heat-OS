from pathlib import Path
import re
p=Path(r"D:\HELIOS\scripts\activate_gemma4_live.py")
s=p.read_text(encoding="utf-8-sig")
print("THINKING_TRUE_ASSIGNMENTS",
      len(re.findall(r'payload\s*\[\s*["\']thinking(?:_enabled)?["\']\s*\]\s*=\s*True',s)))
assert not re.search(r'payload\s*\[\s*["\']thinking(?:_enabled)?["\']\s*\]\s*=\s*True',s)
print("PASS: activation test request is non-thinking")
