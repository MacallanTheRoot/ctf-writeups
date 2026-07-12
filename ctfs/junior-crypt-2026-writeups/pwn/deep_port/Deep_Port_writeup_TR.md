# Junior Crypt 2026 CTF - `Deep Port` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **Kategori:** Pwn
- **Zorluk:** Hard
- **Dosya:** `deep_port`

## Özet

Shipment release işlemi manifest'i free ediyor fakat slot pointer'ını ve boyutunu temizlemiyor. Stale slot hem görüntülenebildiği hem düzenlenebildiği için heap leak, safe-linking hesabı ve tcache poisoning mümkün oluyor.

## Analiz

Program shipment nesneleri ile global `harbor` yapısını yönetiyor. View çıktısı stale manifest pointer'ını ve route function pointer'ını sızdırıyor. Bunlar sırasıyla heap/safe-linking ve text adres hesabını sağlıyor.

Exploit için aynı size class içinde iki chunk free edilir. UAF olan chunk'ın tcache `next` değeri glibc safe-linking formülüne göre hedefe kodlanır:

```text
encoded_next = target XOR (freed_chunk_address >> 12)
```

Tek free yeterli değildir; tcache count sıfıra düştüğünde zehirlenmiş head kullanılmaz. İki freed chunk ile ilk allocation normal chunk'ı, ikincisi zehirlenen hedefi döndürür.

Remote layout'ta en sağlam hedef stale manifest pointer'ına göre bulunan `harbor->dispatch_hook` alanıydı:

```text
target = manifest_pointer - 0x30
print_flag = standby + 0x20
```

Poisoned allocation dispatch hook üzerine geldi. Buraya remote `print_flag` adresi yazıldı ve dispatch menüsü çalıştırılarak flag basıldı.

## Flag

```text
grodno{03786281-13d3-41a1-bcbd-e2bc99b9770f}
```

## Root Cause

Free sonrasında slot metadata'sının temizlenmemesi, edit/view destekli use-after-free ve tcache freelist poisoning sağlıyor.
