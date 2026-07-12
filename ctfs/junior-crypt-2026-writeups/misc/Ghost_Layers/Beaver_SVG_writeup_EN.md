# Junior Crypt 2026 CTF - `Ghost Layers` Writeup

- **Writeup Author:** Efe Sahinbas
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Steganography / SVG  
**Challenge file:** `beaver.svg`  
**Difficulty:** Medium  
**Flag format:** `grodno{...}`

---

## Challenge Description

Author: @vvanuss
medium

What stays visible is not always what matters most.

Flag format: grodno{}

---

## Summary

The SVG contains a visible beaver drawing and a faint text-like layer. The important part is that this faint layer is a trap: it is visible, but it is not the part that matters most.

By inspecting the SVG source instead of only looking at the rendered image, the hidden outlined text group can be found inside the `<defs>` section. The text is converted to paths and referenced through a clip path/mask setup.

Rendering that hidden group separately makes the flag readable:

```text
grodno{9l0ry_t0_Al1v@r1@_9l0ry_t0_b33r}
```

---

## 1. Initial Inspection

The challenge file is a normal SVG:

```bash
file beaver.svg
```

Output:

```text
beaver.svg: SVG Scalable Vector Graphics image
```

The file is not a bitmap image with EXIF metadata or an appended archive. The useful information is inside the XML structure.

---

## 2. Searching the SVG Source

A quick source search for common SVG hiding primitives is useful:

```bash
rg -n "grodno|display|visibility|opacity|hidden|clip|mask|defs|text|path" beaver.svg
```

The SVG contains:

- A `<defs>` section
- A group with `id="s17"`
- A `clipPath` referencing `#s17`
- A `mask`
- Low-opacity decorative geometry

The rendered image shows a beaver and a faint band of text. The hint warns that the visible result can be misleading, so the source structure has to be inspected directly.

---

## 3. The Hidden Text Group

Inside `<defs>`, there is a path-based group:

```xml
<g id="s17">
  <g transform="translate(62.500,454.000) scale(0.009400,-0.009400)"
     fill="#f8efc9" stroke="#f8efc9" stroke-width="36">
    ...
  </g>
</g>
```

This group is then used as a clipping path:

```xml
<clipPath id="cp4">
  <use href="#s17"/>
</clipPath>
```

The letters are not stored as a `<text>` node. They have been converted into many `<path>` elements, so ordinary text extraction will not show the flag.

---

## 4. Rendering the Group Separately

The reliable way to read it is to isolate the group and render it with high contrast.

For example, create a temporary SVG containing only the `s17` group and a `<use href="#s17"/>`, then render it:

```bash
magick textalone.svg textalone.png
```

The isolated layer reveals the intended flag text:

```text
grodno{9l0ry_t0_Al1v@r1@_9l0ry_t0_b33r}
```

The important detail is that the character after each `t` is zero (`0`), not the letter `o`.

---

## 5. Flag

```text
grodno{9l0ry_t0_Al1v@r1@_9l0ry_t0_b33r}
```

---

## Root Cause

The flag is embedded as outlined SVG path geometry and reused through clip/mask rendering. Because the text is converted to paths, it is not visible to normal string searches as plain text.
