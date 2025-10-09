# musescore-sheets

## Issues
Scores that provide PNG files will look lower resolution than scores that provide SVG files. There are two solutions: 
- Algorithmically convert bitmap (png) to a set of vectors (svg) 
    - vtracer, pypotrace
- Upscale the png (increases file size)
    - super-image, cv2

If the Musescore page layout changes the xpaths used will need to be updated

Musescore uses IP-based geolocation, they either intentionally or unintentionally change the xpaths to certain elements if your ip makes
too many requests it seems...
