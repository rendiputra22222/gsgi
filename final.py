from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Setup Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Tidak menampilkan browser
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Gunakan webdriver-manager agar otomatis download ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

PASARAN_DENGAN_SUB = [
    "BRUNEI", "CHELSEA", "TOTO MACAU", "HUAHIN", "KING KONG4D",
    "POIPET", "TOTO MALI", "KENTUCKY", "FLORIDA", "BANGKOK",
    "NEW YORK", "OREGON"
]

PASARAN_TANPA_SUB = [
    "HOKI DRAW", "SINGAPORE", "SYDNEY LOTTO", "PCSO", "NEVADA", "HONGKONG LOTTO",
    "NORTH CAROLINA DAY", "CALIFORNIA", "CAROLINA EVENING",
    "BULLSEYE", "MAGNUM4D", "TOTO CAMBODIA LIVE"
]

def close_popup():
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "mask-close"))).click()
        print("✅ Popup berhasil ditutup!")
        time.sleep(0)  # Tunggu animasi
    except:
        print("⚠️ Tidak ada popup yang muncul.")

def get_lottery_data():
    url = "https://depobos80993.com/#/index?category=lottery"
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    close_popup()

    data_togel = []
    
    for pasaran_name in PASARAN_TANPA_SUB + PASARAN_DENGAN_SUB:
        try:
            pasaran_elements = driver.find_elements(By.CLASS_NAME, "game-item.lottery")
            for pasaran in pasaran_elements:
                name = pasaran.find_element(By.TAG_NAME, "h3").text.strip()
                if name == pasaran_name:
                    print(f"🔍 Mengecek pasaran: {pasaran_name}")
                    driver.execute_script("arguments[0].scrollIntoView();", pasaran)
                    time.sleep(0)
                    
                    if pasaran_name in PASARAN_DENGAN_SUB:
                        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(pasaran))
                        driver.execute_script("arguments[0].click();", pasaran)
                        time.sleep(0)
                        
                        sub_pasarans = driver.find_elements(By.CLASS_NAME, "game-item.lottery")
                        for sub in sub_pasarans:
                            sub_name = sub.find_element(By.TAG_NAME, "h3").text.strip()
                            periode = sub.find_element(By.CLASS_NAME, "game-periodid").text.split(":")[-1].strip()
                            nomor = sub.find_element(By.CLASS_NAME, "lottery-number").text.strip()
                            if nomor:
                                data_togel.append([sub_name, periode, nomor])
                                print(f"✅ Data ditemukan: {sub_name} ({periode}) - {nomor}")
                        
                        try:
                            back_button = driver.find_element(By.CLASS_NAME, "jq-tab-back")
                            driver.execute_script("arguments[0].click();", back_button)
                            time.sleep(0)
                        except:
                            print(f"⚠️ Gagal kembali dari {pasaran_name}")
                    else:
                        periode = pasaran.find_element(By.CLASS_NAME, "game-periodid").text.split(":")[-1].strip()
                        nomor = pasaran.find_element(By.CLASS_NAME, "lottery-number").text.strip()
                        if nomor:
                            data_togel.append([pasaran_name, periode, nomor])
                            print(f"✅ Data ditemukan: {pasaran_name} ({periode}) - {nomor}")
        except:
            print(f"❌ Gagal mengambil data dari {pasaran_name}")
    
    return data_togel

# Ambil data togel
data_togel = get_lottery_data()

driver.quit()

# Urutan yang diinginkan
ORDERED_PASARAN = [
    "TOTO MACAU PAGI", "HUAHIN0100", "BANGKOK 0130", "KENTUCKY MIDDAY", "FLORIDA MIDDAY",
    "NEW YORK MIDDAY", "BRUNEI02", "NORTH CAROLINA DAY", "OREGON 03", "OREGON 06",
    "BANGKOK 0930", "CALIFORNIA", "FLORIDA EVENING", "OREGON 09", "KENTUCKY EVENING",
    "NEW YORK EVENING", "TOTO CAMBODIA LIVE", "CHELSEA11", "CAROLINA EVENING", "BULLSEYE",
    "OREGON 12", "POIPET12", "TOTO MACAU SIANG", "SYDNEY LOTTO", "BRUNEI14", "CHELSEA15",
    "TOTOMALI1530", "POIPET15", "TOTO MACAU SORE", "HUAHIN1630", "SINGAPORE", "MAGNUM4D",
    "TOTO MACAU MALAM 1", "CHELSEA19", "POIPET19", "PCSO", "TOTOMALI2030", "CHELSEA21",
    "HUAHIN2100", "NEVADA", "BRUNEI21", "TOTO MACAU MALAM 2", "POIPET22", "HONGKONG LOTTO",
    "TOTO MACAU MALAM 3", "TOTOMALI2330", "HOKI DRAW", "KING KONG4D MALAM", "KING KONG4D SORE"
]

# Urutkan data sesuai ORDERED_PASARAN
data_togel_sorted = sorted(data_togel, key=lambda x: ORDERED_PASARAN.index(x[0]) if x[0] in ORDERED_PASARAN else len(ORDERED_PASARAN))

# Simpan hasil ke CSV
print("⌛ Menyimpan data di csv local")
df = pd.DataFrame(data_togel_sorted, columns=["Pasaran", "Periode", "Nomor"])
df.to_csv("result.csv", index=False)
print("✅ Semua data berhasil disimpan di csv local")

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Koneksi ke Google Sheets
print("🔄 Menghubungkan ke Google Spreadsheet")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

import json
import os

# Ambil credential dari GitHub Secrets
service_account_info = json.loads(os.getenv("GSPREAD_CREDENTIALS"))
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)

client = gspread.authorize(creds)

# Buka spreadsheet dan worksheet
spreadsheet = client.open("LGT")
worksheet = spreadsheet.worksheet("Sheet1")

# Ambil data lama dari Google Sheets
data = worksheet.get_all_values()
columns = data[0]  # Ambil header
df_sheet = pd.DataFrame(data[1:], columns=columns)

# Baca CSV
df = pd.read_csv("result.csv")

# Normalisasi kolom "Pasaran" di Google Sheets dan CSV
print("✏️ Sedang input data ke Google Spreadsheet")
df_sheet["Pasaran"] = df_sheet["Pasaran"].str.strip().str.upper()
df["Pasaran"] = df["Pasaran"].str.strip().str.upper()

# Pastikan kolom "Nomor" ada dalam df_sheet
if "Nomor" not in df_sheet.columns:
    df_sheet["Nomor"] = ""

# Proses update ke Google Sheets
for index, row in df.iterrows():
    pasaran = row["Pasaran"]
    nomor_baru = str(row["Nomor"]).zfill(4)  # Pastikan angka tetap 4 digit
    
    if pasaran in df_sheet["Pasaran"].values:
        idx = df_sheet[df_sheet["Pasaran"] == pasaran].index[0]
        row_values = worksheet.row_values(idx + 2)  # Ambil semua nilai di baris
        existing_numbers = set(row_values[1:])  # Ambil semua nomor dari kolom kedua ke kanan
        
        if nomor_baru not in existing_numbers:
            col_index = len(row_values) + 1  # Cari kolom kosong berikutnya
            worksheet.update_cell(idx + 2, col_index, f"'{nomor_baru}")  # Update dengan petik satu
    else:
        new_row = [pasaran, f"'{nomor_baru}"]  # Tambahkan petik satu di awal angka
        worksheet.append_row(new_row)

print("✅ Berhasil Input ke database Spreadsheet!")
