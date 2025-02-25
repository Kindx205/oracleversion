import requests
import random
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from faker import Faker
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

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

class TrapAppUI(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        self.url_labels = [Label(text=f"Enter Target URL {i+1}:") for i in range(4)]
        self.url_inputs = [TextInput(text=f"https://example{i+1}.com", multiline=False) for i in range(4)]
        
        for label, input_field in zip(self.url_labels, self.url_inputs):
            layout.add_widget(label)
            layout.add_widget(input_field)
        
        self.bots_label = Label(text="Number of Bots:")
        layout.add_widget(self.bots_label)
        
        self.bots_spinner = Spinner(text="10", values=[str(i) for i in range(1, 101)])
        layout.add_widget(self.bots_spinner)
        
        self.duration_label = Label(text="Visit Duration (Minutes):")
        layout.add_widget(self.duration_label)
        
        self.duration_spinner = Spinner(text="5", values=[str(i) for i in range(1, 21)])
        layout.add_widget(self.duration_spinner)
        
        self.start_button = Button(text="Start Bots")
        self.start_button.bind(on_press=self.start_bots)
        layout.add_widget(self.start_button)
        
        self.stop_button = Button(text="Stop Bots")
        self.stop_button.bind(on_press=self.stop_bots)
        layout.add_widget(self.stop_button)
        
        return layout
    
    def start_bots(self, instance):
        urls = [input_field.text.strip() for input_field in self.url_inputs if input_field.text.strip()]
        if not urls:
            print("Invalid URLs. Please enter at least one valid link.")
            return
        num_bots = int(self.bots_spinner.text)
        duration = int(self.duration_spinner.text) * 60  # Convert minutes to seconds
        print(f"Starting {num_bots} bots across {len(urls)} URLs for {duration//60} minutes")
        threading.Thread(target=run_bots, args=(urls, num_bots, duration)).start()
    
    def stop_bots(self, instance):
        stop_bots()
        print("Bots Stopped")

if __name__ == "__main__":
    TrapAppUI().run()
