# Junior Crypt 2026 CTF - `1000-7` Writeup

- **Author:** Efe Sahinbas
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Misc / MIDI Steganography  
**Challenge file:** `chal.mid`  
**Difficulty:** Medium  
**Flag format:** `grodno{...}`

---

## Challenge Description

> Some melodies stay in your head.  
> Some leave something else behind.

The challenge provides a MIDI file. The wording suggests inspecting data left in the MIDI event stream rather than only listening to the notes.

## 1. File Structure

```bash
file chal.mid
```

The artifact is a valid Standard MIDI format 1 file containing two tracks. The first track is named `Unravel - Tokyo Ghoul`. Since the note events form an ordinary song, the non-note MIDI events are the more interesting hiding place.

## 2. Pitch-bend Anomaly

Parsing the second track reveals 752 pitch-bend events. The most significant data byte of every event has one of only two values:

```text
82, 46, 46, 82, 82, 46, ...
```

Grouping consecutive events produces only `(82, 46)` and `(46, 82)`. Their order encodes one bit:

```text
(82, 46) -> 1
(46, 82) -> 0
```

The 752 events become 376 pairs, or 376 bits. Packing the bits into bytes in MSB-first order yields:

```python
b'\xc0\xde*grodno{U1tr@_m3g@_5up3r_Gul_M1d_SF_1000-7}\xc5\x11'
```

The surrounding bytes are padding/noise; the flag itself is plainly visible.

## 3. Automated Solution

The included solver uses only the Python standard library:

```bash
python3 solver.py chal.mid
```

Output:

```text
grodno{U1tr@_m3g@_5up3r_Gul_M1d_SF_1000-7}
```

## Flag

```text
grodno{U1tr@_m3g@_5up3r_Gul_M1d_SF_1000-7}
```

## Root Cause

The flag is embedded as binary data in the ordering of two values used by consecutive pitch-bend events, not in the audible melody.
