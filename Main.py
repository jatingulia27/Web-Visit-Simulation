import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import os

# Oxylabs proxy credentials
USERNAME = "emirborova_brluB"
PASSWORD = "AmirAmir994994+"
ENDPOINT = "tr-pr.oxylabs.io:30000"

# Log file path
LOG_FILE_PATH = "log.txt"  # Specify your log file path
DB_PATH = "user_agents.db"  # Specify your database path

# Function to configure Oxylabs proxy
def chrome_proxy(user: str, password: str, endpoint: str) -> dict:
    wire_options = {
        "proxy": {
            "http": f"http://{user}:{password}@{endpoint}",
            "https": f"https://{user}:{password}@{endpoint}",
        }
    }
    return wire_options

# Function to create the user agent table if it doesn't exist
def create_user_agent_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mobile_user_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_agent TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Table 'mobile_user_agents' checked/created.")

# Function to get a random user agent from the database
def get_random_user_agent():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_agent FROM mobile_user_agents ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]  # Return the user agent string
    else:
        raise ValueError("No user agents found in the database")

# Function to configure the Selenium browser with proxy and random user agent
def configure_browser():
    print("Configuring browser with proxy and random user agent...")
    
    user_agent = get_random_user_agent()
    proxy_options = chrome_proxy(USERNAME, PASSWORD, ENDPOINT)

    # Configure Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    
    print(f"Using Proxy: {proxy_options['proxy']['http']}")
    print(f"Using User-Agent: {user_agent}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver, user_agent, f"{USERNAME}@{ENDPOINT}"

# Function to log session data
def log_session(proxy, user_agent, max_time, domain):
    log_entry = f"Proxy: {proxy}, User Agent: {user_agent}, Max Time: {max_time:.2f}s, Domain: {domain}\n"
    print(f"Logging session: {log_entry.strip()}")
    
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(log_entry)

# Function to simulate random clicks on elements
def click_random_element(driver):
    try:
        clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a, button, [role='button'], div[onclick], input[type='submit']")
        if clickable_elements:
            element_to_click = random.choice(clickable_elements)
            print(f"Clicking on element: {element_to_click.tag_name}")
            element_to_click.click()
            time.sleep(random.uniform(1, 3))
    except Exception as e:
        print(f"Error while trying to click an element: {e}")

# Function to simulate browsing behavior
def browse_website(driver, domain, min_time, max_time):
    print(f"Navigating to {domain}")
    driver.get(domain)
    
    time_on_page = random.uniform(min_time, max_time)
    print(f"Browsing {domain} for {time_on_page:.2f} seconds.")

    total_height = driver.execute_script("return document.body.scrollHeight")
    scroll_times = random.randint(1, 5)
    print(f"Scrolling {scroll_times} times on the page.")
    for _ in range(scroll_times):
        scroll_position = random.randint(0, total_height - 1)
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        print(f"Scrolled to position: {scroll_position}")
        time.sleep(random.uniform(1, 3))
        click_random_element(driver)
    
    time.sleep(time_on_page)
    print(f"Closing browser after {time_on_page:.2f} seconds of browsing.")
    driver.quit()

# Function to handle concurrent visitors with randomized parameters
def visitor_thread(domain, min_time_range, max_time_range):
    print("Starting a new visitor session...")
    driver, user_agent, proxy = configure_browser()
    
    min_time = random.uniform(*min_time_range)
    max_time = random.uniform(*max_time_range)
    
    browse_website(driver, domain, min_time, max_time)
    log_session(proxy, user_agent, max_time, domain)

# Main function to simulate concurrent visits
def start_simulation(concurrency_range, domain, min_time_range, max_time_range, cooldown_range, target_visits):
    threads = []
    total_visits = 0
    
    while total_visits < target_visits:
        concurrency = random.randint(*concurrency_range)
        print(f"Starting {concurrency} concurrent visitors...")

        if total_visits + concurrency > target_visits:
            concurrency = target_visits - total_visits

        for _ in range(concurrency):
            thread = threading.Thread(target=visitor_thread, args=(domain, min_time_range, max_time_range))
            threads.append(thread)
            thread.start()

            cooldown_time = random.uniform(*cooldown_range)
            print(f"Waiting {cooldown_time:.2f} seconds before starting the next visitor...")
            time.sleep(cooldown_time)

        for thread in threads:
            thread.join()

        total_visits += concurrency
        print(f"Total visits so far: {total_visits}/{target_visits}")

if __name__ == "__main__":
    create_user_agent_table()  # Ensure the table is created
    # Inputs with ranges
    concurrency_range = (1, 3)  # Range of concurrent visitors
    domain = "https://beyondclinic.online/"  # Replace with your target domain
    min_time_range = (1, 2)  # Range for min time spent on the page (seconds)
    max_time_range = (3, 5)  # Range for max time spent on the page (seconds)
    cooldown_range = (1, 3)  # Cooldown between visits (seconds)
    target_visits = 5  # Total number of visits

    # Ensure log file is empty before running the test
    if os.path.exists(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)

    # Start the simulation
    start_simulation(concurrency_range, domain, min_time_range, max_time_range, cooldown_range, target_visits)
