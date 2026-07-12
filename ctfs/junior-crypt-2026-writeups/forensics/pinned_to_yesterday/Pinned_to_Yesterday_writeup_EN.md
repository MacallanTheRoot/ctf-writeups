# Junior Crypt 2026 CTF - `Pinned to Yesterday` Writeup

- **Author:** Efe Sahinbas
- **Category:** Forensics
- **Difficulty:** Medium

## Goal

Recover three values from a Windows artifact set: the first PDF under `RecentDocs\.pdf`, the TypedPaths folder associated with ShellBagsExplorer, and the executable name in the supplied Prefetch sample.

## Registry Analysis

The collection contains several test hives, so raw strings alone are ambiguous. The hives were parsed and the following keys examined:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs\.pdf
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths
```

The PDF entry accepted by the challenge validator is the physically first `.pdf` record:

```text
WhatsNew.2898.pdf
```

The final folder component of the relevant TypedPaths value is:

```text
ShellBagsExplorer
```

## Prefetch Analysis

The Prefetch sample uses `MAM` compression, so its executable name should be read after proper decompression/parsing rather than inferred from unrelated raw strings. The header identifies `CALC.EXE`; the validator expects it as `calc.exe`.

## Flag

```text
grodno{WhatsNew.2898.pdf_ShellBagsExplorer_calc.exe}
```

## Note

Multiple hives and the ambiguity between MRU order and physical registry-value order produced several plausible combinations. The flag above was explicitly accepted by the CTF server.
