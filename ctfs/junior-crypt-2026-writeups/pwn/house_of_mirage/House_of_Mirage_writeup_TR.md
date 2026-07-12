# Junior Crypt 2026 CTF - `House of Mirage` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **Kategori:** Pwn
- **Zorluk:** Medium
- **Dosya:** `house_of_mirage`

## Özet

Arşiv thread'i süresi dolan session'ı temizleyip kendi free-list'ine ekliyor fakat aktif session dizisindeki pointer'ı kaldırmıyor. Aynı chunk bir sink için tekrar kullanıldığında stale session pointer üzerinden canlı sink nesnesi ezilebiliyor.

## Analiz

Binary stripped C++ PIE'dır; Full RELRO, NX ve stack canary açıktır. Session ve sink nesneleri `0x60` bayttır. Gizli flag rutini yerel binary'de PIE tabanına göre `0x3970`, normal session vtable'ı ise `0x6030` offsetindedir.

Exploit zinciri:

```text
session oluştur
-> expiry arm et
-> archive thread session chunk'ını free-list'e alsın
-> sink oluştur ve aynı chunk'ı reuse et
-> stale session profile import ile sink'i overwrite et
-> fake vtable üzerinden hidden replay rutinini çağır
```

Sink yeniden kullanılan chunk'a yerleşince stale session `show`, sink'in gerçek function-table pointer'ını serial gibi sızdırır. Bu leak ile PIE tabanı hesaplanır. Sink'in kendi içinde sahte bir vtable oluşturulur ve ilk entry `PIE + 0x3970` yapılır.

Remote'da archive thread yaklaşık 25 ms aralıkla sink'i tekrar scrub ettiği için sequence yarışa giriyordu. `create sink -> arm stale session -> show stale session` işlemleri tek TCP burst içinde gönderilerek yarış kazanıldı. Ardından stale profile import sink'i overwrite etti ve sink flush dolaylı çağrıyı hidden replay rutinine yönlendirdi.

## Flag

```text
grodno{51154113-985a-4f07-9db7-aba34670946c}
```

## Root Cause

Expiry sırasında aktif pointer'ın temizlenmemesi use-after-free oluşturuyor; yeniden kullanılan nesne stale session API'si üzerinden arbitrary object overwrite'a dönüşüyor.
