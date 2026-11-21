# Kayıp Frekans — OSINT CTF (2026)

**[English](#english) | [Türkçe](#türkçe)**

> **Spoiler warning:** This directory contains a detailed solution write-up and actual challenge flags. Read it only if you want the solutions to the completed competition.

## English

**Event:** Kayıp Frekans, AltaySec OSINT Challenge Season III  
**Date:** 15 September 2026  
**Organizers:** AltaySec × NGN × Kodluyoruz  
**Participant and write-up author:** Hamza Efe Şahinbaş (@MacallanTheRoot)  
**Documented result:** 19/20 solved (author's challenge notes; not a verified leaderboard position)

The challenge told a connected investigation story across six chapters: **Pansiyon → Kasaba → Arşiv → Fener → Hastane → Sabah**, with additional open-source tasks. This write-up documents how I followed the evidence and verified 19 flags. The third regular *Fener* flag remained unsolved; I have not invented an answer for it.

### Techniques covered

| Area | Practical techniques |
| --- | --- |
| Web investigation | HTML/DOM, browser console, network responses, source-code review |
| Audio and radio | DTMF decoding, spectrogram inspection, Morse, SSTV Martin M1 |
| Digital forensics | EXIF/GPS metadata, ZIP comments, Code 128, RGB-LSB steganography |
| Open-source intelligence | Public Git history, YouTube subtitles, Internet Archive metadata |
| Reporting | Evidence trails, exact flag validation, false-positive analysis |

**[Read the complete Turkish write-up](./Kayip_Frekans_Writeup_TR.md)** · [Official competition page](https://kayipfrekans.altaysec.com.tr/) · [Organizer's retrospective](https://akademi.altaysec.com.tr/blog/kayip-frekans-osint-challenge-hikayesi)

### Evidence and reproducibility

This GitHub version preserves the full technical narrative, commands, outputs, and flags. Some commands refer to a local competition-time snapshot at `workspace/linear-story/kayipfrekans-20260915-143018/`; that snapshot and the original challenge files are **not** included in this repository. Those commands illustrate the recorded process rather than constituting a self-contained replay.

Screenshots and derived images referenced by the original write-up are **not redistributed in this text-only GitHub version**. Captions identify where they appeared. The game design and original challenge materials belong to their respective creators; this participant-authored analysis is independent of and not endorsed by the organizers.

## Türkçe

**Yarışma:** Kayıp Frekans — AltaySec OSINT Challenge Sezon III  
**Tarih:** 15 Eylül 2026  
**Düzenleyenler:** AltaySec × NGN × Kodluyoruz  
**Katılımcı ve yazar:** Hamza Efe Şahinbaş (@MacallanTheRoot)  
**Kişisel çözüm kaydı:** 19/20 (resmî sıralama iddiası değildir)

Bu çözüm yazısı Pansiyon, Kasaba, Arşiv, Fener, Hastane ve Sabah bölümleri ile Açık Kaynak görevlerinin inceleme sürecini anlatır. **Fener bölümünün üçüncü normal flag'i çözülememiştir**; buna dair cevap uydurulmamıştır.

**[Türkçe teknik çözümün tamamını oku](./Kayip_Frekans_Writeup_TR.md).**

> **Görseller hakkında:** Orijinal arşivde 10 kanıt görseli bulunmaktadır. GitHub'a yüklenen bu sürüm, organizatöre ait görsel materyali yeniden dağıtmadan metni ve teknik yöntemi paylaşır. Bazı terminal komutları yalnızca yarışma sırasında kaydedilen yerel dosya yolları üzerinden yeniden çalıştırılabilir.