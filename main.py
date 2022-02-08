from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

URL = "https://musescore.com/user/4923276/scores/5516956"

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--incognito')
chrome_options.add_argument("--window-size=1920x10800")
chrome_options.add_argument("start-maximised")

driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

links = driver.find_elements(By.CLASS_NAME, "_2zZ8u").get_attribute("src")