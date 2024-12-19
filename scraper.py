import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import html

# WebDriver'ı başlat
driver = webdriver.Chrome()

# Web sitesine git
site_url = "https://tim.org.tr/tr/ihracat-rakamlari"
driver.get(site_url)

# Gizli elementleri görünür yapmak için JavaScript
driver.execute_script("document.querySelectorAll('.xn-report-item').forEach(el => el.style.display = 'block');")

# Verileri kaydetmek için klasör oluştur
output_folder = "TİM_Datasets"
os.makedirs(output_folder, exist_ok=True)

try:
    # Sayfa tamamen yüklenene kadar bekle
    wait = WebDriverWait(driver, 10)

    # Yıl ve ayların bulunduğu xn-report-item elementlerini bul
    report_items = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "xn-report-item")))

    for item in report_items:
        try:
            # Her bir item için yıl ve ay bilgilerini al
            try:
                year_month = item.find_element(By.TAG_NAME, "h5").text.strip()
            except Exception:
                year_month = "Tarih_Bilinmiyor"

            # Tüm bağlantıları al
            links = item.find_elements(By.XPATH, ".//ul/li/a")
            for link in links:
                # Bağlantının URL'sini ve açıklamasını al
                file_url = link.get_attribute("href")
                if not file_url.startswith("http"):
                    file_url = "https://tim.org.tr" + file_url

                try:
                    file_description = html.unescape(link.text.strip())
                except Exception:
                    file_description = "Açıklama_Bilinmiyor"

                # Yeni dosya adını oluştur
                file_name = f"{year_month} {file_description}.xlsx"
                file_name = file_name.replace(" ", "_").replace("/", "_")
                file_path = os.path.join(output_folder, file_name)

                # Dosyayı indir
                print(f"{file_name} indiriliyor...")
                response = requests.get(file_url)

                # Eğer dosya başarılı şekilde indirildiyse
                if response.status_code == 200:
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    print(f"Dosya kaydedildi: {file_path}")
                else:
                    print(f"Dosya indirilemedi: {file_url} - HTTP Hatası: {response.status_code}")

        except Exception as e:
            print(f"Bir hata oluştu: {e}")

finally:
    # Tarayıcıyı kapat
    driver.quit()
    print("Tarayıcı kapatıldı.")
