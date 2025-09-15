import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import AnimalCol.Functions_find_red as find_particles_module
import AnimalCol.User_loading as User_loading
import AnimalCol.Extracting_particles as Extract_data
import numpy as np

import cv2


#In those tests, we use images with know characteristics to verify that our results are as predicted.

#Used to simplify the tests: create a contour including all the image
def create_general_contours(img):
    height, width = img.shape[:2]
    mask = np.ones((height, width), dtype=np.uint8) * 255
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours



#Testing for particle detection and data exportation
def test_all_white_image():
    img = cv2.imread(User_loading.resource_path(os.path.join("../tests/Images/All_white.png")))
    img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    contours=create_general_contours(img)
    particles = find_particles_module.find_particles(img, contours, 0, [0, 0], [0, 0], [0, 0], 0, 0)
    assert particles == ((), None), "Unexpected particles detected"

def test_black_rectangle_image_not_finding_particle():
    img = cv2.imread(User_loading.resource_path(os.path.join("../tests/Images/Black_rectangle_425px.png")))
    img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    contours=create_general_contours(img)
    particles = find_particles_module.find_particles(img, contours, 0, [10, 20], [0, 0], [0, 0], 0, 0)
    assert particles == ((), None), "Unexpected particles detected"

def test_black_rectangle_image_finding_particle():
    img = cv2.imread(User_loading.resource_path(os.path.join("../tests/Images/Black_rectangle_425px.png")))
    img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    contours=create_general_contours(img)
    particles = find_particles_module.find_particles(img, contours, 0, [0, 0], [0, 0], [0, 0], 0, 0)
    results=Extract_data.extract_data(img,particles,-1,1)
    assert results == (180625, 0, 0, 0, 'NA', 'NA'), "Particles are not following expected pattern"


def test_three_colors_rectangle_image_finding_particle():
    img = cv2.imread(User_loading.resource_path(os.path.join("../tests/Images/Colors_RGB_rectangle_100px.png")))
    img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    contours=create_general_contours(img)
    particles = find_particles_module.find_particles(img, contours, 0, [0, 360], [150, 255], [150, 255], 0, 0)
    results=Extract_data.extract_data(img,particles,-1,1)
    print(results)
    assert results[0] == (30000) and round(results[2],3) == 255 and round(results[3],3) == 255, "Particles are not following expected pattern"


def test_blue_rectangle_image_finding_particle():
    img = cv2.imread(User_loading.resource_path(os.path.join("../tests/Images/Colors_RGB_rectangle_100px.png")))
    img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    contours=create_general_contours(img)
    particles = find_particles_module.find_particles(img, contours, 0, [100, 140], [150, 255], [150, 255], 0, 0)
    results=Extract_data.extract_data(img,particles,-1,1)
    assert results[0] == (10000) and round(results[1],3) == 240 and round(results[2],3) == 255 and round(results[3],3) == 255, "Particles are not following expected pattern"


def test_pierced_rectangle_image_finding_particle():
    img = cv2.imread(User_loading.resource_path(os.path.join("../tests/Images/Colors_RGB_rectangle_100px_hole_50px.png")))
    img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    contours=create_general_contours(img)
    particles = find_particles_module.find_particles(img, contours, 0, [175, 50], [150, 255], [150, 255], 0, 0)
    results=Extract_data.extract_data(img,particles,-1,1)
    assert results[0] == (7500) and round(results[1],3) == 0 and round(results[2],3) == 255 and round(results[3],3) == 255, "Particles are not following expected pattern"



def particle_inside_contour():
    img = cv2.imread(User_loading.resource_path(os.path.join("../tests/Images/Complex_rectangle.png")))
    img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
    img_copy=img.copy()
    img_copy=cv2.cvtColor(img_copy,cv2.COLOR_RGB2GRAY)
    _,img_copy=cv2.threshold(img_copy,200,255,1)
    contours=cv2.findContours(img_copy, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    results_target=Extract_data.extract_data(img, contours,0,1)
    assert results_target[0] == (180625), "Target is not correctly detected"

    #The three particles
    particles = find_particles_module.find_particles(img, contours, 0, [0, 180], [100, 255], [100, 255], 0, 0)
    results=Extract_data.extract_data(img,particles,-1,1)
    assert results[0] == (21807) and results[1]>80 and results[1]<160 , "Particles are not following expected pattern"

    #We remove the darker one
    particles = find_particles_module.find_particles(img, contours, 0, [0, 180], [150, 255], [150, 255], 0, 0)
    results=Extract_data.extract_data(img,particles,-1,1)
    assert results[0] == (16035) and results[1]>80 and results[1]<160 , "Particles are not following expected pattern"

    #Checking their characteristics one by one:
    particles = find_particles_module.find_particles(img, contours, 0, [0, 180], [100, 255], [100, 255], 0, 0)
    assert len(particles[0])==3, "Wrong number of particles detected"

    #On top of image
    results = Extract_data.extract_data(img, particles, 0, 1)
    assert results[0] == (5772)   and  round(results[1],3) == 96 and round(results[2],3) == 255 and round(results[3],3) == round(43.1*2.55)

    results = Extract_data.extract_data(img, particles, 1, 1)
    assert results[0] == (8835)   and  round(results[1],3) == 120 and round(results[2],3) == 255 and round(results[3],3) == 255

    results = Extract_data.extract_data(img, particles, 2, 1)
    assert results[0] == (7200)   and  round(results[1],3) == 70 and round(results[2],3) == 255 and round(results[3],3) == round(79.2*2.55)


particle_inside_contour()
