import json
import re
import time
import random
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup


def get_driver():
    chromedriver_path = "chromedriver.exe"  # or full path if needed
    service = Service(executable_path=chromedriver_path)

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    return webdriver.Chrome(service=service, options=options)

def extract_item_id_from_url(url):
    match = re.search(r'i(\d{8,})', url)
    if match:
        return match.group(1)
    else:
        raise ValueError("❌ Could not find itemId in the URL.")

THAI_ABBR_MONTHS = {
    "ม.ค.": "Jan", "ก.พ.": "Feb", "มี.ค.": "Mar", "เม.ย.": "Apr", "พ.ค.": "May", "มิ.ย.": "Jun",
    "ก.ค.": "Jul", "ส.ค.": "Aug", "ก.ย.": "Sep", "ต.ค.": "Oct", "พ.ย.": "Nov", "ธ.ค.": "Dec"
}

def thai_date_to_datetime(thai_date_str):
    for thai_abbr, eng_abbr in THAI_ABBR_MONTHS.items():
        if thai_abbr in thai_date_str:
            translated_date_str = thai_date_str.replace(thai_abbr, eng_abbr)
            return datetime.strptime(translated_date_str, "%d %b %Y")
    return None

reference_date = datetime.now()

duration_mapping = {
    'ชั่วโมงที่แล้ว': timedelta(hours=-1),
    'นาทีที่แล้ว': timedelta(minutes=-1),
    'วันที่แล้ว': timedelta(days=-1),
    'สัปดาห์ที่แล้ว': timedelta(weeks=-1),
}

def convert_time_interval(interval):
    if interval == 'วันนี้':
        return reference_date.strftime("%d/%m/%Y")
    parts = interval.split()
    if len(parts) == 2:
        try:
            quantity = int(parts[0])
            time_unit = ' '.join(parts[1:])
            if time_unit in duration_mapping:
                return (reference_date + duration_mapping[time_unit] * quantity).strftime("%d/%m/%Y")
        except:
            pass
    try:
        return thai_date_to_datetime(interval).strftime("%d/%m/%Y")
    except:
        return interval

def scrape_review(driver):
    response = driver.execute_script("return document.body.innerHTML;")
    soup = BeautifulSoup(response, 'html.parser')
    return soup.find("pre")

def main_scraper(product_url, product_name):
    itemid = extract_item_id_from_url(product_url)
    df = pd.DataFrame()
    driver = get_driver()

    for i in range(1, 30):
        url = f'https://my.lazada.co.th/pdp/review/getReviewList?itemId={itemid}&pageSize=50&filter=0&sort=0&pageNo={i}'
        try:
            driver.get(url)
        except WebDriverException as e:
            print(f"❌ Cannot load page {i} — Error: {e}")
            break

        hidden_div = scrape_review(driver)
        if hidden_div is None:
            print("⚠️ CAPTCHA likely triggered. You have 15 seconds to solve the slider in browser...")
            time.sleep(15)
            hidden_div = scrape_review(driver)

        if hidden_div:
            try:
                data = json.loads(hidden_div.text)
                if "model" in data and "items" in data["model"]:
                    reviews = data["model"]["items"]
                    if not reviews:
                        print("✅ No more reviews. Exiting...")
                        break

                    df_page = pd.DataFrame([{
                        "username": r.get("buyerName", ""),
                        "options": r.get("skuInfo", ""),
                        "comment": r.get("reviewContent", ""),
                        "rating": r.get("rating", ""),
                        "date": r.get("reviewTime", ""),
                        "product": r.get("itemTitle", "")
                    } for r in reviews])
                    df = pd.concat([df, df_page], ignore_index=True)
                else:
                    print("⚠️ JSON structure invalid.")
                    break
            except Exception as e:
                print(f"🚨 Error on page {i}: {e}")
                break

        time.sleep(random.uniform(5, 10))

    driver.quit()
    df.drop_duplicates(inplace=True)
    df['product'] = product_name
    df['source'] = "Lazada"
    df['date'] = df['date'].apply(convert_time_interval)
    return df
