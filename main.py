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
from webdriver_manager.chrome import ChromeDriverManager

# py main.py [musescore link] "[name of pdf]"

URL = sys.argv[1]
name = sys.argv[2]

print(sys.argv[1])
print(sys.argv[2])

if not sys.argv[1] or not sys.argv[2]:
    print("Missing arguments. Please follow this format:")
    print(r'py main.py [musescore link] "[name of pdf]"')
    sys.exit()

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--incognito')
chrome_options.add_argument("--window-size=1920x10800")
chrome_options.add_argument("start-maximised")

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get(URL)

div = driver.find_elements(By.CSS_SELECTOR, ".vAVs3")

links = []
currentPage = 1
for webEl in div:
	link = webEl.find_element(By.CLASS_NAME, "_2zZ8u").get_attribute("src")
	links.append(link)
	currentPage += 1
driver.quit()

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
print("PDF created!")