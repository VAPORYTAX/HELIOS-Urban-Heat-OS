import argparse, json
from app.exposure.seed import seed_exposure

parser = argparse.ArgumentParser()
parser.add_argument("--reset", action="store_true")
args = parser.parse_args()

print(json.dumps(seed_exposure(reset=args.reset), indent=2))
