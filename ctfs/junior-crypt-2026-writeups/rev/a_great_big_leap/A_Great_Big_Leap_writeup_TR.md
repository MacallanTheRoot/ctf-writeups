# Junior Crypt 2026 CTF - `A Great Big Leap` Writeup

- **Writeup Yazarı:** Efe Şahinbaş
- **Challenge Yazarı:** @meier
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Reverse Engineering  
**Zorluk:** Medium  
**Dosya:** `goingtoofaraway5.exe`  
**SHA-256:** `4250d40739aab526e7b7745820cfc90509135cdb09c868491b0fe53c359d5ac6`

---

## Challenge İpucu

Rusça şiir; tekrar tekrar zıplamayı, kısa süre durmayı, karşılaştırmayı ve ne kadar büyük bir yol gidildiğini söylüyor. Bunlar doğrudan assembly talimatlarına karşılık gelir:

```text
прыжок     -> jmp / conditional jump
стоим      -> nop
сравнить   -> cmp
путь       -> relative branch displacement
```

## 1. İlk İnceleme

```bash
file goingtoofaraway5.exe
objdump -d -Mintel goingtoofaraway5.exe
```

Dosya yalnız üç section içeren, 32-bit ve stripped bir Windows PE dosyasıdır. `.data` bölümü yüzlerce sahte flag benzeri metin içerir. Program bunlardan birkaçını yazdırır ve döngüler oluşturur; bu metinler flag değildir.

## 2. Jump Mesafeleri

x86 relative branch hedefi şu şekilde hesaplanır:

```text
target = address_after_instruction + signed_displacement
```

Bu nedenle kat edilen yol:

```text
distance = abs(target - address_after_instruction)
```

Tüm doğrudan jump talimatları karşılaştırıldığında en büyük branch şudur:

```asm
0040112f: cmp edx, 0x33
00401132: jmp 0x00401014
```

`jmp rel32` beş byte olduğu için jump sonrasındaki adres `0x401137` olur:

```text
0x401137 - 0x401014 = 0x123
```

Şiirde istenen “great big leap”, yani en büyük sıçrama mesafesi `0x123` değeridir.

## 3. Otomatik Çözüm

Eklenen solver PE `.text` bölümünü Capstone ile disassemble eder, bütün direct jump displacement'larını hesaplar ve en büyüğünü hex olarak flag içine yerleştirir:

```bash
python3 solve.py goingtoofaraway5.exe
```

Çıktı:

```text
largest jump: 0x401132 -> 0x401014 (-0x123)
grodno{123}
```

## Flag

```text
grodno{123}
```

## Temel Nokta

Challenge'ın anlamı sahte flag stringlerinde veya gerçek runtime davranışında değil, şiirin tarif ettiği relative jump mesafesindedir.
