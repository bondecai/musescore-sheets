import sys
import re
import time
import os
import tempfile
import undetected_chromedriver as uc # Import for stealth capabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# Removed unused imports from your list for clarity

################################################################################
# Custom function to wait for the download to complete and be stable
################################################################################

def wait_for_download(download_dir, timeout=45):
    """
    Waits for a non-temporary file to appear in the download directory
    and ensures its size is stable before returning the filename.
    Increased timeout to 45 seconds for robustness.
    """
    start_time = time.time()
    # Get initial file list to focus only on new downloads
    initial_files = set(os.listdir(download_dir))
    
    print("⏳ Waiting for download to complete...")
    
    while time.time() - start_time < timeout:
        
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files
        
        if new_files:
            for filename in new_files:
                # 1. Skip temporary/partial download files
                if filename.endswith(('.crdownload', '.part', '.tmp')):
                    continue
                
                filepath = os.path.join(download_dir, filename)
                
                # 2. Check for file stability (CRITICAL for full download)
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    size_1 = os.path.getsize(filepath)
                    time.sleep(1) # Wait 1 second
                    size_2 = os.path.getsize(filepath)
                    
                    if size_1 == size_2:
                        print(f"✅ Download complete! File: {filename}")
                        return filename
                    else:
                        print(f"File size still changing for {filename}, waiting...")
        
        time.sleep(1) # Wait 1 second before re-listing the directory

    print("❌ Download timed out or failed.")
    return None

################################################################################

def main():
    if len(sys.argv) < 2:
        print("Missing arguments. Please follow this format:")
        print(r'py main.py [musescore link]')
        sys.exit()

    URL = sys.argv[1]

    tempDir = tempfile.TemporaryDirectory()
    driver = None 

    try:
        #####################################
        # CORRECTLY DEFINING DOWNLOAD PATHS #
        #####################################
        # Use the absolute path from the tempDir object
        downloadDir = tempDir.name 
        print(f"Using temporary directory for download: {downloadDir}")

        chrome_prefs = {
            # 1. Use the absolute path for prefs
            "download.default_directory": downloadDir, 
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            # 2. Include the generic binary type for widest compatibility
            "browser.helperApps.neverAsk.saveToDisk": "image/png,image/jpeg,application/octet-stream", 
        }

        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", chrome_prefs)
        
        # Standard anti-detection arguments
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # Running in non-headless mode to allow visual debugging if necessary
        # chrome_options.add_argument('--headless') 
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument("--window-size=1920x10800")
        chrome_options.add_argument("start-maximised")
        chrome_options.add_argument("--log-level=3") # Increased log level to suppress more noise

        #####################################
        # DRIVER INITIALIZATION (WITH STEALTH)
        #####################################
        print("Initializing undetected-chromedriver...")
        # Use uc.Chrome for an automated, patched browser (stealth)
        driver = uc.Chrome(options=chrome_options, use_subprocess=True)
        driver.set_window_size(1920, 10800)

        print(f"Using Selenium to access {URL}")
        driver.get(URL)

        #####################################
        # CDP COMMAND (CRITICAL FOR FORCING DOWNLOAD)
        #####################################
        driver.execute_cdp_cmd(
            'Page.setDownloadBehavior',
            {
                'behavior': 'allow', 
                # Use the absolute path for CDP command
                'downloadPath': downloadDir, 
                'eventsEnabled': True
            }
        )

        ################################
        # GET NAME AND LINKS (EXISTING CODE)
        ################################
        illegal_chars_pattern = r'[<>:"/\\|?*\x00-\x1F]'
        try:
            name_element = driver.find_elements(By.XPATH, "/html/body/div[1]/div[1]/section/aside/div[1]/div[1]/h1/span")
            if name_element:
                name = name_element[0].get_attribute('textContent')
                name = re.sub(illegal_chars_pattern, "", name)
            else:
                raise Exception("Name element not found.")
        except Exception as e:
            print(f"Error getting name: {e}")
            print("This usually means the xpath needs to be updated")
            name = input("Enter name manually: ")
        
        links = []
        pages = 0
        for x in range(1, 51):
            webElement = driver.find_elements(By.XPATH, f"/html/body/div[1]/div/section/main/div/div[3]/div/div/div[{x}]/img")
            if len(webElement) <= 0:
                break
            link = webElement[0].get_attribute('src')
            links.append(link)
            pages += 1
        
        print(f"Found sheet with name: {name} and with {pages} pages")
        
        if not links:
            print("No links found. Exiting.")
            return

        ###############################
        # DOWNLOAD LINK0 AND WAIT
        ###############################
        link0 = links[0]
        print(f"Attempting download of link0: {link0}")
        
        # This navigates and triggers the download (forced by CDP)
        driver.get(link0) 
        
        # Use the robust waiting function
        downloaded_filename = wait_for_download(downloadDir) 
        
        if downloaded_filename:
            old_path = os.path.join(downloadDir, downloaded_filename)
            # Save the final file to the current working directory
            final_name = f'{name}_page_0.png'
            new_path = os.path.join(os.getcwd(), final_name) 
            os.rename(old_path, new_path)
            print(f"Success! File saved to current working directory as: {final_name}")
        else:
            print("Download failed or timed out.")
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
    finally:
        if driver:
            print("Quitting Selenium driver.")
            driver.quit()
            
        print(f"Cleaning up temporary directory: {downloadDir}")
        tempDir.cleanup()

if __name__ == '__main__':
    main()