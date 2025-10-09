import sys
import re
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
from reportlab.pdfgen.canvas import Canvas
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


###############################
# HOW TO USE                  #
# py main.py [musescore link] #
###############################

def main():
    if len(sys.argv) < 2:
        print("Missing arguments. Please follow this format:")
        print(r'py main.py [musescore link]')
        sys.exit()

    URL = sys.argv[1]

    #######################
    # SETTING UP SELENIUM #
    #######################
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument("--window-size=1920x10800")
    chrome_options.add_argument("start-maximised")
    chrome_options.add_argument("--log-level=1") # Remove logging messages such as: Created TensorFlow Lite XNNPACK delegate for CPU

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920, 10800)

    print(f"Using Selenium to access {URL}")
    driver.get(URL)

    ################################
    # GET NAME AND NUMBER OF PAGES #
    ################################
    illegal_chars_pattern = r'[<>:"/\\|?*\x00-\x1F]'
    try:
        name = driver.find_elements(By.XPATH, "/html/body/div[1]/div[1]/section/aside/div[1]/div[1]/h1/span")[0].get_attribute('textContent')
        name = re.sub(illegal_chars_pattern, "", name)
    except Exception as e:
        print(f"Error getting name: {e}")
        print("This usually means the xpath needs to be updated")
        name = input("Enter name manually: ")
    
    ####################################################################
    # GET LINKS                                                        #
    # Create a list of download links for each page of the sheet music #
    ####################################################################
    links = []
    pages = 0
    for x in range(1, 51): # Could make this an infinite loop but hard stop at 50 iterations in case
        webElement = driver.find_elements(By.XPATH, f"/html/body/div[1]/div/section/main/div/div[3]/div/div/div[{x}]/img")
        if len(webElement) <= 0:
            break
        link = webElement[0].get_attribute('src')
        links.append(link)
        pages += 1
    print(f"Found sheet with name: {name} and with {pages} pages")
    print(f"Links found: {links}")
    
    # Bypass anti-scraping measure: Cloudflare "Just a moment..." page
    ################################################
    # Getting the first page of the sheet requires #
    # waiting for the full page to load first...   #
    ################################################
    tempDir = tempfile.TemporaryDirectory()
    link0 = links[0]
    driver.get(link0)
    wait = WebDriverWait(driver, 10)
    try:
        print("Checking if musescore provided SVGs")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg")))
        content = driver.page_source
        with open(f'{tempDir.name}/score_0.svg', "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        # Musescore serves the first page of PNG sheets inside an <img> tag
        print(f"Musescore probably didn't provide SVGs: {e}")
        content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img")))
        img_url = content.get_attribute('src')

        # Create a requests session and transfer cookies from Selenium to it
        # This makes the request look like it's coming from the same browser session
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        # Use the session to download the image, which now has the correct cookies
        response = session.get(img_url, allow_redirects=True)
        print(response)
        with open(f'tempfolder/score_0.png', "wb") as f:
            f.write(response.content)
        
    return None
    ##############################################
    # SHEET DOWNLOAD AND CONVERSION TO PDF       #
    # Download sheets into a temporary directory #
    ##############################################

    # "Patch" the setDash method to handle negative dashes
    # the values within an SVG stroke-dasharray attribute cannot be negative
    original_setDash = Canvas.setDash

    # Create patched version
    def patched_setDash(self, array=[], phase=0):
        # Convert negative values to positive
        fixed_array = [abs(x) if x < 0 else x for x in array]
        return original_setDash(self, fixed_array, phase)

    # Monkey patch the Canvas class
    Canvas.setDash = patched_setDash

    page = 1
    if "png" in links[0]:
        print("WARNING: PDF will have lower quality because Musescore provided png's instead of svg's")
        for link in links[1:]:
            r = requests.get(link, allow_redirects=True)
            open(f'tempfolder/score_{page}.png', 'wb').write(r.content)
            page += 1
        for i in range(page):
            with open(f'tempfolder/pg{i+1}.pdf', 'wb') as f:
                f.write(img2pdf.convert(f'tempfolder/score_{i}.png'))
    else:
        print(f"Downloading {name} with {pages} pages (SVG)")
        for link in links[1:]:
            print(f"Downloading: {link}")
            r = requests.get(link, allow_redirects=True)
            open(f'{tempDir.name}/score_{page}.svg', 'wb').write(r.content)
            page += 1
        for i in range(page):
            drawing = svg2rlg(f'{tempDir.name}/score_{i}.svg')
            renderPDF.drawToFile(drawing, f'{tempDir.name}/pg{i+1}.pdf')

    # Merge pdfs 
    writer = PdfWriter()
    for i in range(page):
        reader = PdfReader(f'tempfolder/pg{i+1}.pdf')
        writer.addpages(reader.pages)
    writer.write(f'{name}.pdf')
    print(f"{name}.pdf created!")
    tempDir.cleanup()

    print("Quitting Selenium")
    driver.quit()

main()