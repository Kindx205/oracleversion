import requests
import random
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from faker import Faker
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Initialize Faker for generating random user agents
fake = Faker()

# Event to stop bots
stop_event = threading.Event()

# List of free proxy servers
PROXY_LIST = [
    "45.77.201.248:8080", "103.231.78.36:80", "195.154.255.118:80",
    "51.158.154.173:3128", "138.68.60.8:8080", "165.22.81.30:3128"
]

def get_random_proxy():
    return random.choice(PROXY_LIST)

def human_like_browsing(driver, url, duration):
    driver.get(url)
    time.sleep(random.uniform(5, 10))
    end_time = time.time() + duration
    while time.time() < end_time and not stop_event.is_set():
        links = driver.find_elements("tag name", "a")
        if links:
            random.shuffle(links)
            link = random.choice(links)
            driver.execute_script("arguments[0].scrollIntoView();", link)
            time.sleep(random.uniform(2, 5))
            link.click()
            time.sleep(random.uniform(5, 15))  # Added more variation for natural behavior
        else:
            time.sleep(random.uniform(5, 10))  # Idle time to simulate thinking

def start_bot_visit(url, duration):
    try:
        options = Options()
        options.add_argument(f"user-agent={fake.user_agent()}")
        options.add_argument("--headless=new")
        proxy = get_random_proxy()
        options.add_argument(f"--proxy-server=http://{proxy}")
        driver = webdriver.Chrome(options=options)
        human_like_browsing(driver, url, duration)
        driver.quit()
    except Exception as e:
        print(f"Error starting bot: {e}")

def run_bots(urls, num_bots, duration):
    stop_event.clear()
    threads = []
    for _ in range(num_bots):
        url = random.choice(urls)  # Randomly choose between multiple URLs
        thread = threading.Thread(target=start_bot_visit, args=(url, duration))
        thread.start()
        threads.append(thread)
        time.sleep(random.uniform(1, 3))
    for thread in threads:
        thread.join()

def stop_bots():
    stop_event.set()

@app.route('/start_bots', methods=['POST'])
def start_bots():
    data = request.json
    urls = data.get("urls", [])
    num_bots = data.get("num_bots", 10)
    duration = data.get("duration", 5) * 60  # Convert minutes to seconds
    if not urls:
        return jsonify({"error": "Invalid URLs. Please enter at least one valid link."}), 400
    threading.Thread(target=run_bots, args=(urls, num_bots, duration)).start()
    return jsonify({"message": f"Starting {num_bots} bots across {len(urls)} URLs for {duration//60} minutes"})

@app.route('/stop_bots', methods=['POST'])
def stop_bots_route():
    stop_bots()
    return jsonify({"message": "Bots Stopped"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
