#!/usr/bin/env python3

import collections
import json
import statistics
from pathlib import Path


base = Path(__file__).resolve().parent
packet = bytes.fromhex((base / "packet.hex").read_text().strip())
trace = json.loads((base / "timing_trace.json").read_text())

blocks = [packet[i : i + 16] for i in range(0, len(packet), 16)]
plaintext = bytearray()

for block_number in range(1, len(blocks)):
    recovered = [0] * 16

    for pad in range(1, 17):
        timings = collections.defaultdict(list)
        for row in trace:
            if row["block"] == block_number and row["pad"] == pad:
                timings[row["guess"]].append(row["elapsed_ns"])

        guess = max(timings, key=lambda value: statistics.mean(timings[value]))
        index = 16 - pad
        recovered[index] = guess ^ blocks[block_number - 1][index] ^ pad

    plaintext.extend(recovered)

pad_len = plaintext[-1]
if 0 < pad_len <= 16 and plaintext.endswith(bytes([pad_len]) * pad_len):
    plaintext = plaintext[:-pad_len]

print(plaintext.decode())
