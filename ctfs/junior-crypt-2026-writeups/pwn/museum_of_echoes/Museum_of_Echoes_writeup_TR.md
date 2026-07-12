# Junior Crypt 2026 CTF - `Museum of Echoes` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **Kategori:** Pwn
- **Zorluk:** Hard
- **Dosya:** `museum_of_echoes`

## Özet

Bir `whisper` sergisi daha büyük olan `chorus` türüne dönüştürülebiliyor, ancak heap allocation yeniden boyutlandırılmıyor. Chorus rewrite işlemi eski küçük chunk'ın dışına taşarak yanındaki serginin metadata ve routine pointer'ını eziyor.

## Analiz

Binary'de Full RELRO, NX, PIE ve stack canary açık. Debug sembolleri iki nesne düzenini ve çağrılabilir rutinleri gösteriyor:

```text
whisper_t  -> küçük allocation
chorus_t   -> intro + refrain nedeniyle daha büyük allocation
```

Exploit akışı:

1. Yan yana iki `whisper` sergisi oluşturulur.
2. İlk sergi `chorus` olarak reclassify edilir.
3. İlk sergi chorus olarak rewrite edilerek ikinci chunk'a taşılır.
4. İkinci nesnenin marker alanına `0x4543484f` (`ECHO`) yazılır.
5. İkinci nesnenin perform pointer'ı `grand_finale` adresiyle değiştirilir.
6. İkinci sergi perform edilir.

Remote binary yerel dosyayla byte-identical değildi. Servisten sızan `whisper_perform = 0x401296` ve `chorus_perform = 0x4012cb` adresleri remote text düzenini gösterdi. Kontrollü yakın-adres testi sonucunda `grand_finale = 0x401308` bulundu.

Bozulmuş ikinci sergi perform edildiğinde kontrol `grand_finale()` fonksiyonuna geçti ve `flag.txt` içeriği basıldı.

## Flag

```text
grodno{a5b7cb45-ac23-436a-ae13-851e6f90dcfb}
```

## Root Cause

Type değiştirildiğinde nesnenin heap allocation boyutunun güncellenmemesi, type confusion kaynaklı heap overflow oluşturuyor.
