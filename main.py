import requests
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from pdfrw import PdfReader, PdfWriter
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

pngFlag = False
svgFlag = False
if "png" in links[0]:
	pngFlag = True
else:
	svgFlag = True

page = 0
tempDir = tempfile.TemporaryDirectory()
for links in links:
    r = requests.get(links, allow_redirects=True)
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
name = input("Enter name for the pdf: ")
writer.write(f'{name}.pdf')