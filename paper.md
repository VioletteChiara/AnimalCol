---
title: 'AnimalCol: A tool for quantitative color analysis of digital images'
tags:
  - Python
  - biology
  - image analysis
  - color analysis
  - animal coloration
authors:
  - name: Violette Chiara
    orcid: 0000-0002-3442-5336
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Sin-Yeon Kim
    orcid: 0000-0002-5170-8477
    affiliation: 2

affiliations:
 - name: Museum and Institute of Zoology, Polish Academy of Science, Warsaw, Poland
   index: 1
   ror: 00hx57361
 - name: Grupo Ecoloxía Animal, Torre CACTI, Centro de Investigación Mariña, Universidade de Vigo, Vigo, Spain
   index: 2

date: 16 September 2025
bibliography: paper.bib

---

# Summary

`AnimalCol` is a tool for analyzing animal coloration using standard digital photographs. It is a standalone 
Python program developed for the Windows operating system and comes with a straightforward installer. 
`AnimalCol` relies on several packages: OpenCV for image management and analysis, tkinter for the Graphical 
User Interface (GUI), and scipy for basic descriptive statistics of image characteristics. The `AnimalCol` 
code is open source and available at a GitHub repository (https://github.com/VioletteChiara/AnimalCol) 
where detailed guidelines are provided. A dedicated webpage is also available at 
http://vchiara.eu/index.php/animalcol, where the installer, guidelines and general information are provided.

# Statement of need

Animal coloration has been extensively studied by biologists in both laboratory and field settings. 
For instance, skin, fur, feather, and scale colors play key roles in sexual signaling, establishing social 
status, protection from ultraviolet radiation, predator and parasite avoidance, or thermoregulation 
[@Cuthill:2017]. Unlike microorganisms and plants, obtaining biological samples from animals often raises 
methodological and ethical issues. Therefore, photographic images have become increasingly useful resources for
analyzing variation in animal coloration [@Potash:2020]. To ensure accurate and consistent measurement 
of animal coloration, researchers typically standardize camera position and light conditions, and photograph 
specimens alongside color and scale references. 

Some commercial programs (e.g., Las X and X-Rite Suite) and open-source programs (e.g., Image J and CellProfiler) 
also analyze color in digital images. However, many of these programs are designed for sophisticated analysis of 
high-resolution microscopic images or require additional plugins and customized settings. Thus, `AnimalCol` 
was developed to provide biologists with an open-source, stand-alone, and user-friendly tool for efficiently 
analyzing animal coloration from standard digital photographs.



# Features

Features 
`AnimalCol` features a complete and user-friendly GUI (\autoref{fig:Figure1}) in which color hue, saturation (intensity) 
and value (brightness) charts are presented to help understand the technical characteristics of the 
loaded images. Users can define Regions of Interest (ROIs, \autoref{fig:Figure1}C) and set the scale directly on their
images (\autoref{fig:Figure1}A). `AnimalCol` proposes a project-like organization, which allows users to load and analyze 
a number of images simultaneously within a single project.

`AnimalCol` also features a semi-automatic ROI detection based on background segmentation to rapidly distinguish 
the target animal from the background. Users can also select color characteristics to find all matching regions 
on the image as particles (\autoref{fig:Figure1}D). 

The program exports extracted data as a .csv file, which summarize: i) the ROI’s area and mean color 
characteristics (Hue, Saturation, Value), ii) a summary of the same characteristic for all the particles, iii)
a summary of the same characteristics for each individual particle.


# Examples: Studying the sexual coloration in a fish and an insect

To illustrate the workflow of `AnimalCol`, we show the example of the analysis of red sexual coloration in male 
three-spined sticklebacks’ cheek. The images used and presented in Figure 1 are from [@Chiara:2022]
in which a preliminary version of `AnimalCol` was used. Here, we used `AnimalCol` to calculate for each male the 
area and ratio of red colored surface over the whole-body area. 

Step 1. Project preparation

- Launch `AnimalCol` and create a new project (Project > New)
- Add the images to be used (Images > Add new images)

Step 2. Definition of the ROIs (\autoref{fig:Figure1}C)

- Click the Detection > Automatic target detection menu. 
- Click on the background several times until the fish area is highlighted in pink. Tools of erosion, dilation and 
- surface filters can also be used to improve results.
- Click the “Select all” button in the “Videos” section and validate.
- If necessary, manual correction of the ROIs can be done by clicking on the images.

Step 3. Definition of the Scale (\autoref{fig:Figure1}A)

- Move the two points on the top left corner of the images to set a known distance, for example using a reference 
scale on the image. 
- Fill in the “Real life distance" entry on the top right corner of the program with the known distance between 
the two points.

Step 4. Particles detection and extraction

- Use the color chart to select the color of interest (in the example, hue 340–60, saturation 100–255, and value
25–255, \autoref{fig:Figure1}E).
- Click the “Validate all” button. 
- In the main menu, select Detection>Export particles and select a destination location. The results will be saved as
.csv file.

The ranking of the fish according to the red ratio can be seen on \autoref{fig:Figure1}. 

![Illustration of AnimalCol interface. A) Scale information defined by user. B) 
Color references used to ensure that all pictures were taken in similar context. C) 
ROI delimitation. D) Particles found by the program that match the color settings. E) 
Color settings defined by the user. F) Image displayed in the miniature showing the picture before 
applying AnimalCol color selection.\label{fig:Figure1}](Figures/Figure1.png)

`AnimalCol` can also be used for numerous purposes such as counting spots, calculating the mean hue value 
of ROIs, the intensity of specific areas, etc. In \autoref{fig:Figure2}, we illustrate how damselflies are ranked 
according to their thorax mean hue analyzed by `AnimalCol` (images from @Sanmartin:2017). 


![Damselflies ranked according to the AnimalCol results of the average hue 
value on their thorax (from left to right, and top to bottom). In this species, males have only a 
blue phenotype, while females have green or blue phenotype.\label{fig:Figure2}](Figures/Figure2.png)


# Acknowledgements

We gratefully acknowledge Dr. Iago Sanmartín-Villar for kindly providing the images used to illustrate
the program features. SYK was supported by the Ministerio de Ciencia e Innovación 
(MCIN/AEI/10.13039/501100011033, project PID2022-138503NB-I00).

# References