"""
Minimal usage example for flowmeter.

Install:
    pip install -e tools/flowmeter/     # from the repo root
    # or on an edge device:
    pip install dpkt
    # then copy the flowmeter/ directory alongside your script

Run this file:
    python tools/flowmeter/example.py capture.pcap
"""

import sys
import time
from flowmeter import convert_pcap_to_csv

if len(sys.argv) < 2:
    print("Usage: python example.py <input.pcap> [output.csv]")
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else "flows.csv"

t0 = time.perf_counter()
n_flows = convert_pcap_to_csv(input_path, output_path)
elapsed = time.perf_counter() - t0

print(f"Wrote {n_flows} flows to {output_path!r} in {elapsed:.2f}s")
