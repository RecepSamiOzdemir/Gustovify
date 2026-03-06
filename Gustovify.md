# 📔 Gustovify: Kapsamlı Teknik Tasarım ve Sistem Spesifikasyonları

| Bilgi | Detay |
| :--- | :--- |
| **Sürüm** | 1.2 |
| **Durum** | Stratejik Planlama, Mimari Detaylandırma ve Uygulama Projeksiyonu |
| **Hazırlayan** | Gustovify Sistem Mimarları ve Geliştirme Kurulu |

---

## 1. Giriş, Felsefi Temeller ve Misyon Bildirisi
Gustovify; konvansiyonel yemek tarifi uygulamalarının ötesinde, mutfak faaliyetlerini bütünsel bir yaklaşımla optimize eden bir **dijital asistan ekosistemidir**. 

* **Sorun:** Mutfaktaki "uygulama" ve "envanter yönetimi" arasındaki kopukluk, verimlilik kaybına ve gıda israfına yol açmaktadır.
* **Çözüm:** Kullanıcı envanter verilerini (Kiler) sistematik takip ederek, bu verilere en uygun gastronomik seçenekleri sunan bir "Mutfak Yönetim Mekanizması" tesis etmek.
* **Yaklaşım:** Tarifleri sadece okunabilir metinler değil, **işlenebilir veri setleri** olarak ele alır. "Pişirme Modu" ile operasyonel zorlukları teknolojik entegrasyonla asgariye indirmeyi hedefler.

---

## 2. Kullanıcı Etkileşim Tasarımı ve Estetik İlkeler

### 2.1. Fonksiyonel ve Ergonomik Tasarım Prensipleri
Arayüz mimarisi; mutfak ortamındaki yüksek nem, buhar ve gıda artıklarıyla temas eden eller gibi fiziksel kısıtlamalar göz önünde bulundurularak hazırlanmıştır.

* **Dokunmatik Optimizasyon:** Buton boyutları ve aralıkları, standart mobil UI rehberlerinden %20 daha geniş tutulmuştur.
* **Sesli Geri Bildirim:** Kullanıcı müdahalesinin kısıtlı olduğu anlarda kritik bilgilerin sesli iletilebilmesi için erişilebilirlik katmanı güçlendirilmiştir.

### 2.2. Görsel Stil Konfigürasyonları
Kullanım konforu sağlamak maksadıyla sistem üç ana görsel şablon ihtiva etmektedir:

1.  **Minimalist Yapı (The Purist):** Gün ışığının yoğun olduğu mutfaklarda kontrastı artırarak okunabilirliği maksimize eden nötr tonlar.
2.  **Tematik Karanlık Mod (The Alchemist):** Düşük ışıklı ortamlarda göz yorgunluğunu azaltan, altın ve kehribar vurgulu yapı. Biyolojik ritmi korumayı hedefler.
3.  **Geleneksel Arşiv Modu (The Traditionalist):** Parşömen kağıdı efektleri ve klasik serif tipografi ile geleneksel yemek defteri estetiği.

### 2.3. Ana Panel (Dashboard) Bileşenleri
* **Dinamik Bilgilendirme:** Günün saati, mevsimsel ürünler ve SKT'si yaklaşan kiler verileri.
* **Odaklanmış Öneri:** Envanterle %90 ve üzeri korelasyon gösteren tarifleri öne çıkaran mekanizma.
* **Operasyonel Kontrol:** "Randomizer", içerik filtreleme (vejetaryen vb.) ve hızlı veri giriş butonları.

---

## 3. Sistemsel Modüller ve Algoritmalar

### 3.1. Veri Edinimi ve AI Entegrasyonu
* **Smart Scraper:** Web tariflerinin DOM yapısını analiz ederek reklam ve gereksiz içerikleri temizler, sadece malzeme ve talimatları yapılandırılmış veriye dönüştürür.
* **Dijitalleştirme (OCR):** El yazısı tarifleri tanıma ve düşük ışıkta gürültü azaltma (denoising) algoritmaları.
* **Semantik Temizleme:** Elde edilen veriler "Yerel Dil Modelleri" (On-device LLM) ile anlamlandırılır; örneğin "bir adet soğan" parametrik bir objeye dönüştürülür.

### 3.2. Envanter Yönetimi ve Analitik Öngörüler
* **Gelişmiş Kiler Takibi:** Statik (baharat/sos) ve dinamik (süt/et) envanter ayrımı.
* **Kritik Eşik Uyarıları:** Azalan ürünleri algılar ve alışveriş listesine otomatik eklemeyi teklif eder.
* **Otomatik Senkronizasyon:** Pişirme sonrası kullanılan miktarların stoktan gerçek zamanlı düşülmesi için onay alır.

### 3.3. Uygulama Safhası ve Pişirme Modu
* **Hiyerarşik İlerleme:** Her adımın ekranın tamamını kapladığı adım odaklı navigasyon.
* **Wakelock Protokolü:** Mutfak faaliyeti esnasında cihazın uyku moduna geçmesi yazılımsal olarak engellenir.
* **Etkileşimli Zamanlayıcılar:** Adım içindeki sürelere otomatik tanımlanan ve tek dokunuşla başlatılabilen dijital sayaçlar.

---

## 4. Teknik Spesifikasyonlar ve Güvenlik

### 4.1. Çevrimdışı Öncelikli Mimari (Offline-First)
* **Veri Depolama:** Tüm operasyonel veriler cihaz üzerinde şifrelenmiş bir SQLite veri tabanında muhafaza edilir.
* **Bulut Senkronizasyonu:** Çevrimiçi olunduğunda veriler TLS 1.3 protokolü ile aktarılır; çakışmalar "Last Write Wins" veya kullanıcı onayı ile çözülür.

### 4.2. Dinamik Ölçeklendirme ve Birim Dönüştürme
* **Hassas Skalalandırma:** Porsiyon değişikliğinde miktarlar orantılanır; "3.3 yumurta" gibi sonuçlar mutfak standartlarına yuvarlanır.
* **Esnek Birim Yönetimi:** "Bir tutam" gibi standart dışı ifadeler risk nedeniyle orantılama dışı bırakılır ve "Özel Birim" olarak sunulur.

---

## 5. Veri Gizliliği ve Etik Standartlar
* **Anonimleştirme:** Tüketim alışkanlıkları kişisel kimlik bilgilerinden (PII) tamamen arındırılır.
* **Data Ethics Dashboard:** Kullanıcıların veri paylaşımını şeffafça görebileceği ve yönetebileceği panel.

---

## 6. Stratejik Gelişim ve Uygulama Projeksiyonu

| Faz | Odak Alanı | Teknik ve Operasyonel Hedefler |
| :--- | :--- | :--- |
| **Faz 1** | Temel Mimari | Kimlik doğrulama, temel CRUD işlemleri, şifreli yerel depolama ve senkronizasyon. |
| **Faz 2** | Akıllı Modüller | AI tabanlı Scraper, kiler-tarif eşleştirme motoru ve birim dönüştürücü kararlılığı. |
| **Faz 3** | Kullanıcı Deneyimi | Pişirme Modu v2 (sesli geri bildirim), OCR stabilizasyonu ve profesyonel raporlama. |
| **Faz 4** | Ekosistem Genişlemesi | Perakende API entegrasyonu, sosyal paylaşım katmanı ve topluluk özellikleri. |

---

## 7. Veri Paylaşımı ve Taşınabilirlik Standartları
* **Semantik Veri Çıktısı (JSON-LD):** Schema.org standartlarına uygun dışa aktarma.
* **Evrensel PDF/A:** Seçilen temanın estetiğini ve yüksek kontrastı koruyan arşiv kalitesinde çıktılar.
* **Hızlı Transfer (QR Portability):** Tariflerin kullanıcılar arasında saniyeler içinde aktarılması için sıkıştırılmış dinamik QR kodlar.

---
> **Sonuç Notu:** Bu doküman, Gustovify projesinin teknik, idari ve etik süreçlerinde "Yegane Referans Kaynağı" (Single Source of Truth) mahiyetindedir.