#!/usr/bin/env python3
import base64
import hashlib
import io
import itertools
import pickle
from pathlib import Path


WORDS = (b"snow", b"candle", b"tangerine", b"clock")


class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) == ("payload", "install_supply_chain_probe"):
            return lambda cipher, weights, seal: (cipher, weights, seal)
        raise pickle.UnpicklingError(f"blocked global: {module}.{name}")


def stream(key, size):
    output = bytearray()
    counter = 0
    while len(output) < size:
        output.extend(
            hashlib.blake2s(key + counter.to_bytes(2, "little")).digest()
        )
        counter += 1
    return bytes(output[:size])


def main():
    model_path = Path(__file__).with_name("model.pkl")
    cipher, weights, seal = SafeUnpickler(io.BytesIO(model_path.read_bytes())).load()

    for history in itertools.product(WORDS, repeat=4):
        sequence = b"|".join(history)
        if hashlib.sha256(sequence).digest() != seal:
            continue

        key = hashlib.blake2s(weights + sequence + b"inference-cache").digest()
        plain = bytes(
            left ^ right
            for left, right in zip(cipher, stream(key, len(cipher)))
        )
        print(f"history: {sequence.decode()}")
        print(f"ticket: {base64.b85encode(plain).decode()}")
        print(f"flag: {plain.decode()}")
        return

    raise RuntimeError("no matching history found")


if __name__ == "__main__":
    main()

