# Junior Crypt 2026 — `Invisible Editor` Writeup

- **Author:** Efe Şahinbaş
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Forensics / Misc  
**Target:** `invisible_editor.docx`  
**Challenge description:**

Author: @vvanuss
easy

My teammate sent me a file with a flag, but I can't see it. Help me find it.

Flag format: grodno{}

---

## Summary

The challenge provides a Microsoft Word document (`invisible_editor.docx`). When opened in Word, the text is just "Did you see the flag?" and the flag itself is completely hidden from normal view. However, because `.docx` files are essentially ZIP archives containing XML files, the actual flag could be found by extracting the document and inspecting the raw XML contents.

Final flag:

```text
grodno{F1@g_W@5_H3r3_0nc3}
```

---

## 1. Initial Recon

Opening the `invisible_editor.docx` file reveals only a short piece of text: "Did you see the flag?". There was no obvious hidden text, white text on white background, or other simple Word tricks visible at first glance. 

This indicated that the flag might be hidden deeper within the file structure or the document properties.

---

## 2. Inspecting the DOCX Archive

Since `.docx` files are ZIP archives, the best approach is to unzip the file to view its raw components:

```bash
unzip invisible_editor.docx -d extracted_docx
```

This reveals standard Word document directories, including:
- `word/`
- `docProps/`
- `_rels/`

---

## 3. Extracting the Flag

The primary content of a Word document is stored in `word/document.xml`. By extracting the text from this XML file and stripping out all the formatting tags, the document history and hidden text can be revealed.

Running a simple search for the flag format (`grodno{`) on the raw XML contents exposed the hidden flag:

```bash
cat word/document.xml | sed -e 's/<[^>]*>//g' | grep -i grodno
```

This returned the hidden string: `grodno{F1@g_W@5_H3r3_0nc3}`.

---

## 4. Conclusion

This challenge demonstrates that office documents can retain hidden data, revision history, and metadata not visible in standard viewing modes. By treating the DOCX file as an archive and inspecting its raw XML, the concealed flag was easily recovered.

Final flag:

```text
grodno{F1@g_W@5_H3r3_0nc3}
```
