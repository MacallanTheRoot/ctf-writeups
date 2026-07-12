# NoHackNoCTF 2026 — `67 Login System` Writeup

- **Yazar:** Efe Şahinbaş
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Web / Reverse Engineering  
**Hedef:** `http://chal2.teagod.tech:8003/`  
**Challenge açıklaması:**

```text
Who is Whois?
http://chal2.teagod.tech:8003/

This is not a part of challenge don't break it
```

---

## Özet

Bu challenge ilk bakışta sıradan bir login sistemi gibi görünüyordu. Ana sayfa yalnızca giriş ekranına yönlendiriyor, login sayfası ise klasik bir kullanıcı adı / parola formu sunuyordu. Ancak formun kendisi gerçek çözüm noktası değildi.

Sayfa üzerindeki en önemli ipucu şuydu:

```text
This is a demonstration login; any credentials will succeed.
```

Bu ifade, challenge’ın bir kullanıcı adı veya parola kırma problemi olmadığını gösteriyordu. Frontend tarafındaki login akışı sadece dekoratifti. Asıl kontrol, backend uygulamasının içine gömülü token/secret mantığında saklanıyordu.

Çözüm, uygulamanın yayın dosyalarını inceleyip ASP.NET backend içindeki mantığı okumaya dayanıyordu.

Final flag:

```text
NHNC{gggggggggggggggggggggggggggggggggggggggggggggggggggg_sixseven!!!}
```

---

## 1. İlk Keşif

Servise bağlandığımda ana sayfada doğrudan hassas bir bilgi yoktu. Sayfa yalnızca kullanıcıyı login ekranına yönlendiriyordu.

Login sayfası klasik bir formdan oluşuyordu:

- Username alanı
- Password alanı
- `POST /login` isteği
- Basit bir “Sign in” akışı

İlk bakışta brute-force, SQL injection veya klasik authentication bypass gibi yollar denenebilir gibi duruyordu. Ancak HTML içinde görünen açıklama, bu yönde zaman kaybetmemek gerektiğini gösterdi.

```text
This is a demonstration login; any credentials will succeed.
```

Bu nedenle problem, “doğru şifreyi bulmak” değil; login işlemi sonrası backend’in hangi iç kontrolü yaptığını anlamaktı.

---

## 2. Frontend’in Rolü

Login formu herhangi bir credential ile başarılı olabilecek şekilde tasarlanmıştı. Bu durum, frontend’in gerçek bir güvenlik katmanı olmadığını gösteriyordu.

Burada çıkarılan temel sonuç şuydu:

```text
Frontend yalnızca kullanıcı akışını göstermek için var.
Gerçek challenge mantığı backend tarafında.
```

Bu yüzden tarayıcıda formu tekrar tekrar denemek yerine challenge dosyalarını incelemek daha mantıklıydı.

---

## 3. Challenge Dosyalarını İnceleme

Challenge dosyaları incelendiğinde bunun bir ASP.NET yayın çıktısı olduğu görüldü. Dikkat çeken dosyalar şunlardı:

```text
Login-page.dll
Login-page.deps.json
Login-page.runtimeconfig.json
wwwroot/index.html
wwwroot/login.html
```

`wwwroot` içindeki HTML dosyaları frontend’i oluşturuyordu. Ancak asıl iş mantığı `Login-page.dll` içinde bulunuyordu.

`Dockerfile` tarafında da uygulamanın doğrudan şu şekilde çalıştırıldığı anlaşılıyordu:

```bash
dotnet Login-page.dll
```

Bu bilgi, analiz yönünü netleştirdi: çözüm için frontend dosyalarından çok `.dll` içindeki backend mantığına bakmak gerekiyordu.

---

## 4. DLL Üzerinde String Analizi

İlk aşamada binary/dll üzerinde string taraması yaptım. Bu tarz .NET challenge’larda string analizi çoğu zaman endpoint isimlerini, route yapılarını, secret değişkenlerini veya token mekanizmalarını ortaya çıkarabilir.

Dikkat çeken string’ler şunlardı:

```text
tokenStore
token
adminSecret
MapGet
MapPost
```

Bu string’ler birkaç önemli noktayı gösteriyordu:

1. Uygulama bir token saklama yapısı kullanıyor.
2. `adminSecret` isminde özel bir değer veya kontrol değişkeni var.
3. Uygulama route tabanlı bir ASP.NET minimal API yapısı kullanıyor olabilir.
4. Flag’e ulaşmak için login formundan ziyade token/secret akışını anlamak gerekiyor.

---

## 5. Backend Mantığının Yorumlanması

`MapGet` ve `MapPost` string’leri, uygulamada route tanımlarının backend içinde yapıldığını gösteriyordu. Bu da login sayfasının sadece statik HTML olmadığını; arka tarafta belirli endpoint’lerin token veya secret üzerinden karar verdiğini düşündürdü.

Bu noktada challenge’ın mantığı şu şekilde özetlenebilir:

```text
1. Kullanıcı herhangi bir credential ile login olur.
2. Backend bir token veya state üretir.
3. Admin/secret kontrolü bu token akışı üzerinden yapılır.
4. Doğru iç değere ulaşıldığında flag döndürülür.
```

Yani hedef, parola kırmak değil; backend’in “kim admin kabul ediliyor?” sorusuna nasıl cevap verdiğini anlamaktı.

Challenge başlığındaki `Who is Whois?` ifadesi de bu noktada anlam kazanıyor. Soru doğrudan kullanıcı adından çok, backend’in kimlik/rol kararını nasıl verdiğine yönlendiriyor.

---

## 6. Neden Klasik Login Saldırısı Değil?

Bu challenge’da aşağıdaki yaklaşımlar asıl çözüm yolu değildi:

- Username/password brute-force
- Basit SQL injection
- Sadece HTML manipülasyonu
- Form action değiştirme
- Cookie değerini rastgele deneme

Çünkü challenge zaten herhangi bir credential ile login olunabileceğini söylüyordu. Bu yüzden doğru yaklaşım, login işleminden sonra backend’de oluşan token/secret akışını analiz etmekti.

---

## 7. Flag’in Elde Edilmesi

Backend mantığı incelendiğinde token/secret akışının flag’e götüren asıl kontrol olduğu anlaşıldı. Doğru değer doğrulandıktan sonra nihai flag şu şekilde elde edildi:

```text
NHNC{gggggggggggggggggggggggggggggggggggggggggggggggggggg_sixseven!!!}
```

---

## 8. Sonuç

Bu challenge dışarıdan basit bir login formu gibi görünse de aslında web + reverse engineering karışımı bir problemdi.

Çözüm adımları özetle şunlardı:

```text
1. Ana sayfa ve login formu incelendi.
2. Login formunun gerçek authentication kontrolü yapmadığı fark edildi.
3. ASP.NET yayın dosyaları analiz edildi.
4. Login-page.dll içinde string analizi yapıldı.
5. tokenStore, token, adminSecret, MapGet ve MapPost izleri bulundu.
6. Backend’in token/secret tabanlı çalıştığı anlaşıldı.
7. Doğru değer doğrulanarak flag elde edildi.
```

Final flag:

```text
NHNC{gggggggggggggggggggggggggggggggggggggggggggggggggggg_sixseven!!!}
```

---

## Not

Bu tarz challenge’larda frontend her zaman gerçek problemi temsil etmez. Özellikle “any credentials will succeed” gibi bir ifade varsa, login formu genellikle yalnızca bir dikkat dağıtıcıdır. Asıl değerli bilgi backend kodunda, route tanımlarında, token üretiminde veya secret karşılaştırmalarında bulunur.
