import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_end_to_end import build_replay

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "output", "sample_replay.json.gz")
with gzip.open(out, "wt", encoding="utf-8") as f:
    json.dump(build_replay(), f)
print("wrote", out, os.path.getsize(out), "bytes")
