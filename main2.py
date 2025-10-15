import sys
from utils.driver_manager import *
from utils.utils import *
import tempfile

BOLD = '\033[1m'
END = '\033[0m'

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

    print(f"{BOLD}Creating Selenium driver{END}")
    driver = create_web_driver()
    print(f"{BOLD}Using Selenium to access{END} {URL}")
    driver.get(URL)
    print(f"{BOLD}Attempting to get name...{END}")
    name = get_name(driver)
    print(f"{BOLD}Name:{END} {name}")
    print(f"{BOLD}Attempting to get links and pages...{END}")
    links, pages = get_links_and_pages(driver)
    print(f"{BOLD}Pages:{END} {pages}")
    print(f"{BOLD}Links:{END} {links}")

    print(f"{BOLD}Creating temporary directory...{END}")
    tempDir = tempfile.TemporaryDirectory()
    print(f"{BOLD}Created temporary directory:{END} {tempDir.name}")


    if "svg" in links[0]:
        print(f"Downloading {name} with {pages} pages from {URL}")
        create_pdfs_svg(driver, tempDir, links, pages, name)
        print("Merging PDFs")
        merge_pdfs(name, pages, tempDir)
        print("Cleaning up")
        cleanup(tempDir, driver)
    elif "png" in links[0]:
        print("WARNING: PDF will have lower quality because Musescore provided png's instead of svg's")
        print(f"Downloading {name} with {pages} pages from {URL}")
        create_pdfs_png(driver, tempDir, links, None, None)
        print("Merging PDFs")
        merge_pdfs(name, pages, tempDir)
        print("Cleaning up")
        cleanup(tempDir, driver)




    return None
    
if __name__ == '__main__':
    main()