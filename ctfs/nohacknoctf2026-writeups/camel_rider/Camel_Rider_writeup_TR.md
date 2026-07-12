# NoHackNoCTF 2026 — Camel Rider Writeup

- **Yazar:** Efe Şahinbaş
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Jail / Sandbox Escape  
**Challenge:** Camel Rider  
**İpucu:** `flag.txt`  
**Amaç:** Kısıtlı Perl ortamından `flag.txt` dosyasını okumak.

---

## Özet

Camel Rider, Perl tabanlı bir jail challenge’ıydı. Uzak servis kullanıcıdan Perl kodu alıyor ve bu kodu kısıtlı bir ortamda çalıştırıyordu. Ancak klasik dosya okuma ve komut çalıştırma fonksiyonları filtrelenmişti. `open`, `read`, `sysread`, `system`, `exec`, `eval`, `readpipe` ve `do` gibi kelimeler kullanıldığında servis isteği engelliyor ve filtre cevabı döndürüyordu.

Çözüm, `open` fonksiyonunu doğrudan çağırmak değildi. Bunun yerine Perl’ün diamond operator’ı olan `<>` ve özel `@ARGV` dizisi kullanıldı. `@ARGV` içine `flag.txt` yerleştirildiğinde, Perl `<>` ifadesini değerlendirirken bu değeri dosya adı olarak ele alır ve dosyayı arka planda kendisi açar.

Final payload:

```perl
BEGIN{@ARGV=(q{flag.txt}); print <>}
```

Flag:

```text
NHNC{Jf8fnibf7fhiqfwbqubFmoyt4191qv3rH}
```

---

## 1. İlk Analiz

Servise bağlanıldığında challenge, kısıtlanmış bir Perl interpreter gibi davranıyordu. Kullanıcıdan bir satır Perl kodu alıyor, çalıştırıyor ve çıktıyı geri döndürüyordu.

Challenge ipucu oldukça doğrudandı:

```text
flag.txt
```

Bu yüzden hedef açıktı: jail içinden `flag.txt` dosyasını okuyabilmek.

İlk denenen klasik Perl dosya okuma yöntemleri engellendi:

```perl
open my $fh, '<', 'flag.txt'; print <$fh>;
```

```perl
print `cat flag.txt`;
```

```perl
system('cat flag.txt');
```

Tehlikeli kelimeler kullanıldığında servis şu tarz bir cevap veriyordu:

```text
Meow
```

Bu da challenge’ın dosya adını bulma problemi olmadığını, asıl meselenin filtreyi aşacak uygun bir Perl davranışı bulmak olduğunu gösterdi.

---

## 2. Filtreyi Anlamak

Filtre, yaygın dosya okuma ve komut çalıştırma primitive’lerini engelliyor gibi görünüyordu:

```text
open
read
sysread
system
exec
eval
readpipe
do
```

Dinamik string oluşturma, fonksiyon adını parçalayarak çağırma veya substitution tabanlı bypass denemeleri de güvenilir sonuç vermedi. Ya doğrudan filtreye takılıyordu ya da runtime ortamı tarafından engelleniyordu.

Buradaki kritik nokta şuydu: Perl’de dosya okumak için her zaman açıkça `open` yazmak gerekmez. Dilin bazı yerleşik davranışları dosya açma işlemini arka planda yapabilir.

Bu challenge için işe yarayan primitive Perl’ün diamond operator’ıydı:

```perl
<>
```

---

## 3. Perl Diamond Operator Mantığı

Perl’de diamond operator genellikle satır satır input okumak için kullanılır:

```perl
while (<>) {
    print $_;
}
```

Eğer açık bir filehandle verilmezse, `<>` özel `@ARGV` dizisine bakar. `@ARGV` içinde dosya adları varsa Perl bu dosyaları sırayla açar ve içeriklerini okur. Eğer `@ARGV` boşsa standart input’tan okur.

Bu davranış challenge’ın kilit noktasıydı.

Yani şunu yazmamıza gerek yoktu:

```perl
open(...)
```

Bunun yerine şunu yapabiliyoruz:

```perl
@ARGV = ('flag.txt');
```

Sonrasında:

```perl
<>
```

ifadesi çalıştırıldığında Perl, `flag.txt` dosyasını dolaylı olarak açıp okuyor.

---

## 4. Payload’ın Kurulması

Temel fikir şu şekildeydi:

```perl
@ARGV=('flag.txt'); print <>
```

Ancak jail ortamında payload’ın daha temiz ve hızlı çalışması için bunu `BEGIN` bloğu içine aldım:

```perl
BEGIN{@ARGV=(q{flag.txt}); print <>}
```

Parça parça açıklarsak:

```perl
BEGIN { ... }
```

Kod compile edilir edilmez bu bloğu çalıştırır. Jail ortamlarında ilgili işlemi hemen tetiklemek için kullanışlıdır.

```perl
@ARGV=(q{flag.txt})
```

Perl’ün argüman listesini hedef dosya adıyla değiştirir. `q{...}` Perl’de tek tırnak benzeri quoting operatörüdür; normal tırnak kullanmadan string yazmayı sağlar.

```perl
print <>
```

Diamond operator’ı çalıştırır. `@ARGV` içinde `flag.txt` bulunduğu için Perl bu dosyayı arka planda açar, okur ve içeriğini ekrana basar.

---

## 5. Exploit

Final payload:

```perl
BEGIN{@ARGV=(q{flag.txt}); print <>}
```

Bu payload servise gönderildiğinde interpreter, `@ARGV` ve `<>` mekanizması üzerinden `flag.txt` dosyasını okudu ve flag’i döndürdü.

---

## 6. Flag

```text
NHNC{Jf8fnibf7fhiqfwbqubFmoyt4191qv3rH}
```

---

## Root Cause

Jail, dosya erişimini engellemek için `open`, `read` ve komut çalıştırma fonksiyonları gibi açık tehlikeli kelimeleri filtreliyordu. Ancak Perl’ün `@ARGV` ve diamond operator üzerinden yaptığı dolaylı dosya okuma davranışı hesaba katılmamıştı.

Bu yüzden, yasaklı bir dosya I/O fonksiyonunu doğrudan yazmadan dosya okunabildi.

---

## Mitigation

Gerçek bir sandbox için keyword filtering güvenli bir yöntem değildir. Perl gibi dillerde özel değişkenler, alternatif syntax biçimleri ve implicit davranışlar basit string filtrelerini kolayca aşabilir.

Alınabilecek önlemler:

1. Kullanıcı kontrollü Perl kodunu doğrudan çalıştırma.
2. Untrusted kodu güçlü şekilde izole edilmiş container veya VM içinde çalıştır.
3. Dosya sistemi erişimini OS seviyesinde kısıtla.
4. Mümkünse seccomp, AppArmor veya SELinux benzeri mekanizmalar kullan.
5. Denylist tabanlı keyword filtrelerine güvenme.
6. Sadece küçük bir dil alt kümesi gerekiyorsa allowlist tabanlı parser kullan.

---

## Son Notlar

Bu challenge kısa ama temiz bir Perl jail örneğiydi. Ana fikir, engellenen işlemi doğrudan çağırmak yerine Perl’ün kendi implicit davranışını kullanmaktı. `@ARGV` ve `<>` birlikte kullanıldığında, interpreter dosyayı kendisi açıp okuyordu.

Final cevap:

```text
NHNC{Jf8fnibf7fhiqfwbqubFmoyt4191qv3rH}
```
