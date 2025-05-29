Scout Agent Kullanıcı El Kitapçığı
 1. Giriş
 Scout Agent, web üzerinden veri toplayan ve görselleştirme yapan bir yazılımdır. Bu el kitapçığı 
yazılımın kurulumunu, kullanımını ve dikkat edilmesi gereken noktaları açıklar.
 2. Sistem Gereksinimleri
 Python 3.9 veya üzeri
 pip / virtualenv
 Internet bağlantısı
 3. Kurulum Adımları
 git clone https://github.com/kullanici_adi/scout-agent.git
 cd scout-agent
 python -m venv venv
 source venv/bin/activate # Windows için: venv\Scripts\activate
 pip install -r requirements.txt
 4. Veritabanı Ayarları
 python scraper.py
 6. Kullanım Senaryosu
 1. 
2. 
3. 
Scraper başlatılır.
 Veriler toplanır ve veritabanına kaydedilir.
 Analiz ve görselleştirme modülü ile sonuçlar incelenebilir.
 7. Hatalar ve Çözüm Önerileri
 Bağlantı hatası: Internet bağlantınızı kontrol edin.
 Modül bulunamadı hatası: pip install -r requirements.txt komutunu tekrar çalıştırın.
 8. Geliştirici Bilgileri
 Geliştiriciler: Furkan Sünney,Veysel Sayar,Bahri İkiz
 Mail: 212802091@ogr.cbu.edu.tr,212802022@ogr.cbu.edu.tr,222802054@ogr.cbu.edu.tr
 Okul: Manisa Celal Bayar Üniversitesi, Yazılım Mühendisliğ
