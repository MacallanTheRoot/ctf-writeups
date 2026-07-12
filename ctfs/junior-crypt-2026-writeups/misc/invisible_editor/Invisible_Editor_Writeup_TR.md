# Junior Crypt 2026 — `Invisible Editor` Çözümü

- **Yazar:** Efe Şahinbaş
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Forensics (Adli Bilişim) / Misc  
**Hedef:** `invisible_editor.docx`  
**Soru Açıklaması:**

Author: @vvanuss
easy

My teammate sent me a file with a flag, but I can't see it. Help me find it.

Flag format: grodno{} 


---

## Özet

Bu soruda bize bir Microsoft Word belgesi (`invisible_editor.docx`) verilmişti. Belge Word'de açıldığında ekranda sadece "Did you see the flag?" yazıyordu ve bayrak (flag) normal görünümde tamamen gizlenmişti. Ancak, `.docx` dosyaları aslında XML dosyalarını barındıran ZIP arşivleri olduğu için, asıl bayrağı belgeyi çıkartıp ham XML içeriğini inceleyerek bulabildik.

Bulunan bayrak:

```text
grodno{F1@g_W@5_H3r3_0nc3}
```

---

## 1. İlk İnceleme (Recon)

`invisible_editor.docx` dosyasını açtığımızda sadece kısa bir metin görüyorduk: "Did you see the flag?". İlk bakışta göze çarpan beyaz arka plan üzerinde beyaz yazı veya basit bir gizleme hilesi yoktu.

Bu durum, bayrağın dosya yapısının veya belge özelliklerinin daha derinlerinde saklanmış olabileceğine işaret ediyordu.

---

## 2. DOCX Arşivinin İncelenmesi

`.docx` dosyaları özünde ZIP arşivleri olduğundan, en iyi yaklaşım dosyayı klasöre çıkartıp ham bileşenlerini görmekti:

```bash
unzip invisible_editor.docx -d extracted_docx
```

Bu işlem sonucunda standart Word belgesi dizinleri ortaya çıktı, örneğin:
- `word/`
- `docProps/`
- `_rels/`

---

## 3. Bayrağın Çıkartılması

Bir Word belgesinin ana içeriği `word/document.xml` dosyasında saklanır. Bu XML dosyasındaki metni çıkarıp tüm biçimlendirme etiketlerini temizlediğimizde, belge geçmişi ve gizli metinler görünür hale gelir.

Ham XML içeriğinde bayrak formatını (`grodno{`) aramak, gizlenmiş bayrağı doğrudan ortaya çıkardı:

```bash
cat word/document.xml | sed -e 's/<[^>]*>//g' | grep -i grodno
```

Çıktı bize gizli metni verdi: `grodno{F1@g_W@5_H3r3_0nc3}`.

---

## 4. Sonuç

Bu soru, ofis belgelerinin standart görüntüleme modlarında görünmeyen gizli verileri, revizyon geçmişlerini ve metadataları barındırabildiğini göstermektedir. DOCX dosyasını bir arşiv gibi ele alıp ham XML yapısını inceleyerek gizli bayrağı kolaylıkla kurtardık.

Final flag:

```text
grodno{F1@g_W@5_H3r3_0nc3}
```
