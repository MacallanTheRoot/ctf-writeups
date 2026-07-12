#!/usr/bin/env python3
"""Recover the WrongKube++ flag from its extracted validator DLL."""

import argparse
import pefile


IMAGE_ADDRESS = 0x18002B310
FLAG_LENGTH = 45


def rva_bytes(pe, address, size):
    rva = address - pe.OPTIONAL_HEADER.ImageBase
    return pe.get_data(rva, size)


def recover(path):
    pe = pefile.PE(path)
    encrypted = rva_bytes(pe, IMAGE_ADDRESS, FLAG_LENGTH)

    seed = 0xC5B1D2FF
    index = 1
    step = 0x49
    state_a = 0x47502943
    state_b = 0x47502932
    state_c = 0x3C6EF35F
    pair_index = 0
    output = bytearray()

    while len(output) < FLAG_LENGTH:
        stream = (seed * 0x19660D + state_c) & 0xFFFFFFFF
        key = ((step - 0x49) ^ (stream >> 16) ^ stream) & 0xFF
        output.append(encrypted[index - 1] ^ key)
        if len(output) == FLAG_LENGTH:
            break

        mixed = (seed * 0x17385CA9) & 0xFFFFFFFF
        seed = (pair_index + ((pair_index | 1) << 4) + 1 + state_b + mixed) & 0xFFFFFFFF
        mixed = (mixed + state_a) & 0xFFFFFFFF
        key = ((mixed >> 16) ^ step ^ mixed) & 0xFF
        output.append(encrypted[index] ^ key)

        pair_index += 2
        index += 2
        step = (step + 0x92) & 0xFFFFFFFF
        state_a = (state_a + 0x35F8DDC) & 0xFFFFFFFF
        state_b = (state_b + 0x35F8DBA) & 0xFFFFFFFF
        state_c = (state_c + 0x22) & 0xFFFFFFFF

    return output.decode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dll", help="extracted wrongkube_validator.dll")
    args = parser.parse_args()
    print(recover(args.dll))
