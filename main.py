from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://musescore.com/user/4923276/scores/5516956"

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--incognito')
chrome_options.add_argument("--window-size=1920x10800")
chrome_options.add_argument("start-maximised")

# driver = webdriver.Chrome(options=chrome_options)
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get(URL)

div = driver.find_elements(By.CSS_SELECTOR, ".vAVs3")
print(div)

svgs = []
currentPage = 1
for webEl in div:
	# print(f"Starting page {currentPage}")
	svgLink = webEl.find_element(By.CLASS_NAME, "_2zZ8u").get_attribute("src")
	svgs.append(svgLink)
	currentPage += 1
driver.quit()

pngFlag = False
svgFlag = False
if "png" in svgs[0]:
	pngFlag = True
else:
	svgFlag = True

# PRINTS LINKS TO SVG FILES
print("Links to svgs")
for link in svgs:
	print(link)

# links = driver.find_elements(By.CLASS_NAME, "_2zZ8u").get_attribute("src")