# Junior Crypt 2026 CTF - `Zakviel` Writeup

- **Author:** Efe Sahinbas
- **Category:** Web
- **Difficulty:** Hard

## Summary

The service runs Thalassa CMS `0.3.75` with a challenge-specific legacy archive import bridge. Imported comment text reaches Thalassa's macro-expansion stage without sanitization, resulting in arbitrary file read.

## Discovery

The landing page emphasizes a legacy import protocol. Comparing the service with the upstream Thalassa source showed that this bridge was custom. The special path is activated with:

```text
folio=archive-17
```

This flow bypasses anonymous-submission and premoderation controls, writes the imported comment into the source tree, and regenerates the static page.

## Macro Injection

Thalassa processes content through `MacroexpandHFContents`. Its file-reading macro is:

```text
%[readfile:PATH]
```

Placing this expression in a legacy-import comment causes the generator to treat attacker input as trusted template content. Reading `/etc/hostname` first confirmed the primitive.

The generator's working directory was enumerated through `/proc/self/cwd`. After locating the private catalogue file, the same `readfile` macro exposed its contents and the flag.

## Flag

```text
grodno{aec40f27-0b38-4012-bc63-c1fcadc2d28f}
```

## Root Cause

Untrusted legacy comment data is passed to the privileged static-site generator with template macros still enabled.
