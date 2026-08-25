import argparse,json
from app.thermal.seed import seed
p=argparse.ArgumentParser(); p.add_argument('--reset',action='store_true'); a=p.parse_args(); print(json.dumps(seed(a.reset),indent=2))
