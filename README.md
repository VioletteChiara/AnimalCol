# AnimalCol
AnimalCol is a user-friendly program whose aim is to facilitate coloration-related image analysis. It has been designed by and for biologists to facilitate the handling of numerous pictures at the same time while ensuring robustness and repeatability.

# User manual
A user manual is available in the root of the repository: https://github.com/VioletteChiara/AnimalCol/blob/main/Guidelines_v2.1.0.pdf

# General information
AnimalCol is a Python-based software designed for the Windows operating system, distributed with an installation package to facilitate deployment. Its functionality depends on several external libraries, most notably OpenCV, which provides tools for image processing and analysis; tkinter, employed for the construction of the graphical user interface (GUI); and SciPy, which is used to derive fundamental descriptive statistics related to image features.

# How to cite
If you are using AnimalCol for your research, please cite: 

Chiara, V., & Kim, S.-Y. (2026). AnimalCol: A tool for quantitative color analysis of digital images. Zenodo. https://doi.org/10.5281/zenodo.20107897

# Automated tests
This project uses pytest for automated testing.
All tests are stored in the tests/ directory.

Each test loads simplified images (in tests/Images/) and checks particle detection under controlled conditions (e.g., an all-white image should return no particles).
