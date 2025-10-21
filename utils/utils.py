import re
from selenium.webdriver.common.by import By
from pdfrw import PdfReader, PdfWriter
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import requests
import img2pdf
from reportlab.pdfgen.canvas import Canvas
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.upscale import *

def get_name(driver):
    illegal_chars_pattern = r'[<>:"/\\|?*\x00-\x1F]'
    try:
        name = driver.find_elements(By.XPATH, "/html/body/div[1]/div[1]/section/aside/div[1]/div[1]/h1/span")[0].get_attribute('textContent')
        name = re.sub(illegal_chars_pattern, "", name)
    except Exception as e:
        print(f"Error getting name: {e}")
        print("This usually means the xpath needs to be updated")
        name = input("Enter name manually: ")
    return name

def get_links_and_pages(driver):
    links = []
    pages = 0
    for x in range(1, 51): # Could make this an infinite loop but hard stop at 50 iterations in case
        webElement = driver.find_elements(By.XPATH, f"/html/body/div[1]/div/section/main/div/div[3]/div/div/div[{x}]/img")
        if len(webElement) <= 0:
            break
        link = webElement[0].get_attribute('src')
        links.append(link)
        pages += 1
    return links, pages

def create_pdfs_svg(driver, tempDir, links):
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

    link0 = links[0]
    driver.get(link0)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg")))
    content = driver.page_source
    with open(f'{tempDir.name}/score_0.svg', "w", encoding="utf-8") as f:
        f.write(content)

    page = 1
    for link in links[1:]:
        print(f"Downloading: {link}")
        r = requests.get(link, allow_redirects=True)
        open(f'{tempDir.name}/score_{page}.svg', 'wb').write(r.content)
        page += 1
    for i in range(page):
        print(f"Converting {tempDir.name}/score_{i}.svg to PDF")
        drawing = svg2rlg(f'{tempDir.name}/score_{i}.svg')
        renderPDF.drawToFile(drawing, f'{tempDir.name}/pg{i+1}.pdf')

    return None

def create_pdfs_png(driver, tempDir, links):
    link0 = links[0]
    driver.get(link0)
    image = driver.find_element(By.TAG_NAME, "img")
    screenshot_path = f"{tempDir.name}/score_0.png"
    if image.screenshot(screenshot_path):
        page = 1
        for link in links[1:]:
            r = requests.get(link, allow_redirects=True)
            open(f'{tempDir.name}/score_{page}.png', 'wb').write(r.content)
            page += 1

        # Upscale image
        for i in range(page):
            upscaled_img = upscale_and_sharpen(f'{tempDir.name}/score_{i}.png', scale_factor=2, sharpen_amount=0.5, sharpen_radius=3)
            cv2.imwrite(f'{tempDir.name}/score_{i}.png', upscaled_img)

        for i in range(page):
            with open(f'{tempDir.name}/pg{i+1}.pdf', 'wb') as f:
                f.write(img2pdf.convert(f'{tempDir.name}/score_{i}.png'))
    else:
        print("Failed to download the first page...")
        print("Aborting")
        return None


    return None

def merge_pdfs(name, pages, tempDir):
    writer = PdfWriter()
    for i in range(pages):
        reader = PdfReader(f'{tempDir.name}/pg{i+1}.pdf')
        writer.addpages(reader.pages)
    writer.write(f'{name}.pdf')
    print(f"{name}.pdf created!")
    return None

def cleanup(tempDir, driver):
    tempDir.cleanup()
    print("Deleting temporary directory")
    driver.quit()
    print("Quitting Selenium")
    return None