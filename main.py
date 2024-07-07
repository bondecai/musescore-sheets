import sys
import requests
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from pdfrw import PdfReader, PdfWriter
import img2pdf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# py main.py [musescore link]

if len(sys.argv) < 2:
    print("Missing arguments. Please follow this format:")
    print(r'py main.py [musescore link]')
    sys.exit()

URL = sys.argv[1]

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--incognito')
chrome_options.add_argument("--window-size=1920x10800")
chrome_options.add_argument("start-maximised")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_window_size(1920, 10800)

driver.get(URL)

# Get name and page number of sheet
name = driver.find_elements(By.XPATH, "/html/body/div[1]/div/section/aside/div[1]/h1/span")[0].get_attribute('textContent')
pages = driver.find_elements(By.XPATH, "/html/body/div[1]/div/section/aside/div[5]/div[2]/table/tbody/tr[1]/td/div")[0].get_attribute('textContent')

# Create a list of download links for each page of the sheet music
links = []
for x in range(1, int(pages)+1):
    webElement = driver.find_elements(By.XPATH, f"/html/body/div[1]/div/section/main/div/div[3]/div/div/div[{x}]/img")
    link = webElement[0].get_attribute('src')
    links.append(link)

# No need for Selenium anymore
driver.quit()

# Download sheets into a temporary directory
page = 0
tempDir = tempfile.TemporaryDirectory()
if "png" in links[0]:
    print("WARNING: PDF will have lower quality because Musescore provided png's instead of svg's")
    for link in links:
        r = requests.get(link, allow_redirects=True)
        open(f'{tempDir.name}/score_{page}.png', 'wb').write(r.content)
        page += 1
    for i in range(page):
        with open(f'{tempDir.name}/pg{i+1}.pdf', 'wb') as f:
            f.write(img2pdf.convert(f'{tempDir.name}/score_{i}.png'))
else:
    for link in links:
        r = requests.get(link, allow_redirects=True)
        open(f'{tempDir.name}/score_{page}.svg', 'wb').write(r.content)
        page += 1
    for i in range(page):
        drawing = svg2rlg(f'{tempDir.name}/score_{i}.svg')
        renderPDF.drawToFile(drawing, f'{tempDir.name}/pg{i+1}.pdf')

# Merge pdfs 
writer = PdfWriter()
for i in range(page):
    reader = PdfReader(f'{tempDir.name}/pg{i+1}.pdf')
    writer.addpages(reader.pages)
writer.write(f'{name}.pdf')
print(f"{name}.pdf created!")
tempDir.cleanup()
