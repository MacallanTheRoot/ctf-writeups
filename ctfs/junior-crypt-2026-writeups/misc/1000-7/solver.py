#!/usr/bin/env python3
"""Decode the flag hidden in paired MIDI pitch-bend events."""

import struct
import sys
from pathlib import Path


def read_vlq(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    while True:
        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 0x7F)
        if byte < 0x80:
            return value, offset


def tracks(data: bytes):
    if data[:4] != b"MThd":
        raise ValueError("not a Standard MIDI file")
    header_length = struct.unpack(">I", data[4:8])[0]
    offset = 8 + header_length
    while offset < len(data):
        chunk_type = data[offset : offset + 4]
        length = struct.unpack(">I", data[offset + 4 : offset + 8])[0]
        chunk = data[offset + 8 : offset + 8 + length]
        offset += 8 + length
        if chunk_type == b"MTrk":
            yield chunk


def pitch_bend_msb(track: bytes) -> list[int]:
    values = []
    offset = 0
    running_status = None
    while offset < len(track):
        _, offset = read_vlq(track, offset)
        status = track[offset]
        if status < 0x80:
            if running_status is None:
                raise ValueError("invalid running status")
            status = running_status
        else:
            offset += 1
            if status < 0xF0:
                running_status = status

        if status == 0xFF:
            meta_type = track[offset]
            offset += 1
            length, offset = read_vlq(track, offset)
            offset += length
            if meta_type == 0x2F:
                break
        elif status in (0xF0, 0xF7):
            length, offset = read_vlq(track, offset)
            offset += length
        else:
            event_type = status & 0xF0
            argument_count = 1 if event_type in (0xC0, 0xD0) else 2
            arguments = track[offset : offset + argument_count]
            offset += argument_count
            if event_type == 0xE0:
                values.append(arguments[1])
    return values


def decode(path: Path) -> bytes:
    values = []
    for track in tracks(path.read_bytes()):
        values.extend(pitch_bend_msb(track))
    if len(values) % 2:
        raise ValueError("unpaired pitch-bend event")

    mapping = {(82, 46): 1, (46, 82): 0}
    bits = []
    for offset in range(0, len(values), 2):
        pair = tuple(values[offset : offset + 2])
        if pair not in mapping:
            raise ValueError(f"unexpected pitch-bend pair: {pair}")
        bits.append(mapping[pair])

    output = bytearray()
    for offset in range(0, len(bits) - 7, 8):
        byte = 0
        for bit in bits[offset : offset + 8]:
            byte = (byte << 1) | bit
        output.append(byte)
    return bytes(output)


if __name__ == "__main__":
    midi_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("chal.mid")
    decoded = decode(midi_path)
    start = decoded.find(b"grodno{")
    end = decoded.find(b"}", start)
    if start < 0 or end < 0:
        raise SystemExit(f"flag not found in decoded bytes: {decoded!r}")
    print(decoded[start : end + 1].decode())
