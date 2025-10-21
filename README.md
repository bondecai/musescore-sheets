# musescore-sheets

A Python utility to download sheet music scores from MuseScore.com and merge them into a single, high-quality PDF document.

## Features

  * **Intelligent Source Detection:** Automatically detects whether the score pages are provided as high-quality **SVG** files or lower-quality **PNG** images.
  * **High-Quality PDF Generation:**
      * **SVG Scores:** Converts source SVGs directly to PDF pages for perfect, scalable vector resolution.
      * **PNG Scores:** **Upscales and sharpens** the images using the `cv2.INTER_LANCZOS4` interpolation and a simple **Unsharp Mask** algorithm to improve print quality
  * **Automated Workflow:** Uses a headless Chrome browser via **Selenium** to navigate the MuseScore page and extract image links.
  * **Dynamic Metadata:** Extracts the score's name from the MuseScore page to automatically name the final PDF file.

-----

## Installation and Setup

### Prerequisites

1.  **Python:** Python 3.13.2

### Step 1: Clone the Repository

Navigate to the directory where you want to store the project and clone the repository:

```bash
git clone https://github.com/bondecai/musescore-sheets.git
cd musescore-sheets
```

### Step 2: Install Dependencies

This project requires several Python libraries listed in the requirements.txt file. Install them using pip:

```bash
pip install requirements.txt
```

-----

## How to Use

Run the script from your terminal, providing the full URL of the MuseScore page as the sole command-line argument:

```bash
python main.py [musescore_score_link]
```

### Example

```bash
python main.py https://musescore.com/user/123456/scores/7890123
```

The script will handle the entire process:

1.  A **headless** Chrome browser is launched to load the MuseScore page.
2.  The score's **name** and **image links** for all pages are extracted.
3.  Pages are downloaded to a **temporary directory**.
4.  Pages are converted/enhanced and merged into a single PDF, saved in the directory where the script was run.
5.  The temporary files are **cleaned up**, and the browser is closed.

-----

## Known Issues and Limitations

This project primarily faces challenges related to MuseScore's changing page structure and image handling.

| Issue | Technical Detail / Cause | Workaround Implemented |
| :--- | :--- | :--- |
| **Outdated XPaths** | The script relies on specific `XPath` patterns to locate the score name and image links. If MuseScore's page layout changes, these XPaths will need to be updated. | The script will ask for the name manually if the extraction fails. |
| **IP-Based Geolocation Changes** | MuseScore may intentionally or unintentionally change element XPaths if your IP address makes too many requests. | If the script breaks, check if the XPaths in `utils.py` are still valid. |
| **Lower Quality PNGs** | Some scores provide lower-resolution PNG files instead of scalable SVG files. | The script automatically applies an image enhancement filter (`upscale.py`) to upscale and sharpen PNGs before PDF conversion to improve print quality. |
| **SVG Rendering Errors** | Negative values in an SVG's `stroke-dasharray` attribute can cause issues with PDF rendering libraries. | The `create_pdfs_svg` function includes a **monkey-patch** for the `reportlab` library to convert negative dash values to positive ones, preventing conversion errors. |

-----