# Junior Crypt 2026 CTF - `Clockwork Vault` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **Kategori:** Pwn
- **Zorluk:** Medium
- **Dosya:** `clockwork_vault`

## Özet

Program global bir mekanizma dizisini yönetiyor. İndeks kontrolü yalnızca üst sınırı denetliyor; negatif indeksler kabul ediliyor. Böylece diziden önce duran `service_cookie` ve aktif servis slotuna erişilebiliyor.

## Analiz

Binary'de NX, PIE ve Full RELRO açık, stack canary yok. Semboller `slots`, `service_cookie`, `idle_cycle`, `trigger_alarm` ve `open_vault` fonksiyonlarını doğrudan gösteriyor.

`inspect_slot()` ve `retune_slot()` şu mantıksal hataya sahip:

```c
if (index >= SLOT_COUNT)
    reject();
// index < 0 kontrolü yok
slot = &slots[index];
```

`inspect -2`, pointer encoding için kullanılan cookie'yi; `inspect -1` ise servis döngüsünün kullandığı encoded action pointer'ını sızdırıyor. Pointer ilişkisi:

```text
encoded_action = service_cookie XOR function_address
```

Remote build yerelden farklı olduğu için adresi yalnız yerel PIE offsetinden hesaplamak güvenilir değildi. Remote'da mevcut idle pointer çözüldü:

```text
idle_cycle = leaked_encoded_action XOR service_cookie
```

`trigger_alarm` ile overwrite primitive'i doğrulandı. Ardından yakındaki `open_vault` adresi belirlendi ve `-1` slotu şu değerlerle yeniden ayarlandı:

```text
setting       = vault magic
encoded_action = service_cookie XOR open_vault
```

Servis döngüsü çalıştırıldığında dolaylı çağrı `open_vault()` fonksiyonuna gitti ve flag basıldı.

## Flag

```text
grodno{7e167a02-b1f1-409c-976d-5717470a22d6}
```

## Root Cause

Signed indeks için alt sınır kontrolünün olmaması, global dizinin öncesinden bilgi sızıntısı ve fonksiyon pointer overwrite sağlıyor.
