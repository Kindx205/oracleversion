from flask import Flask, request, jsonify
import random
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Get environment variables
API_KEY = os.getenv("CAPTCHA_API_KEY", "your-default-key")

# Configure undetected Chrome Driver
ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")  # Run in headless mode for Koyeb

def get_free_proxies():
    proxy_list = []
    try:
        response = requests.get("https://www.sslproxies.org/", timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.select("table tbody tr"):
            columns = row.find_all("td")
            if len(columns) > 1:
                proxy = f"{columns[0].text}:{columns[1].text}"
                proxy_list.append(proxy)
    except:
        pass
    return proxy_list[:10]

def get_driver(proxy=None):
    options = Options()
    options.add_argument(f"--user-agent={ua.random}")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
    return uc.Chrome(options=options)

def search_and_visit(driver, query, target_url):
    driver.get("https://www.google.com")
    time.sleep(random.uniform(2, 4))
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    time.sleep(random.uniform(1, 3))
    search_box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(3, 6))
    
    links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
    for link in links:
        try:
            url = link.get_attribute("href")
            if target_url in url:
                driver.get(url)
                return True
        except:
            continue
    return False

def visit_target(target_url, visits):
    count = 0
    while count < visits:
        proxy = random.choice(get_free_proxies())
        driver = get_driver(proxy)
        query = "best writing platforms"
        success = search_and_visit(driver, query, target_url)
        if success:
            count += 1
        driver.quit()
        time.sleep(random.uniform(60, 180))
    return count

@app.route("/run", methods=["POST"])
def run_bot():
    data = request.json
    target_url = data.get("target_url")
    visits = data.get("visits", 10)
    
    thread = threading.Thread(target=visit_target, args=(target_url, visits))
    thread.start()
    return jsonify({"status": "Bot started", "target": target_url, "visits": visits})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
