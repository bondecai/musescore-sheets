from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_web_driver():
    # Chrome Options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument("--window-size=1920x10800")
    chrome_options.add_argument("start-maximised")
    chrome_options.add_argument("--log-level=1") # Remove logging messages such as: Created TensorFlow Lite XNNPACK delegate for CPU
    
    # Install Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920, 10800) # Load all the pages
    
    return driver

def quit_driver(driver):
    driver.quit()