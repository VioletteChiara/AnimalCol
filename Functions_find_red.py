import cv2
import numpy as np
from scipy.interpolate import splprep, splev


def find_fish(image):
    source_img_grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    ret, Binary_image = cv2.threshold(source_img_grey, 50, 255, cv2.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    Binary_image = cv2.erode(Binary_image, kernel, iterations=3)
    Binary_image = cv2.dilate(Binary_image, kernel, iterations=7)
    Binary_image = cv2.erode(Binary_image, kernel, iterations=2)

    contours, _ = cv2.findContours(Binary_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    filtered_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        M = cv2.moments(cnt)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        if cX > 730 and cX < 3500 and cY > 900 and cY < 2300:
            if area > 50000 and area < 1000000:
                filtered_contours.append(cnt)

    smoothened=[]
    for cnt in filtered_contours:
        x, y = cnt.T
        # Convert from numpy arrays to normal arrays
        x = x.tolist()[0]
        y = y.tolist()[0]
        # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.interpolate.splprep.html
        tck, u = splprep([x, y], k=3, u=None, s=1.0, per=1)
        # https://docs.scipy.org/doc/numpy-1.10.1/reference/generated/numpy.linspace.html
        u_new = np.linspace(u.min(), u.max(), 50)
        # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.interpolate.splev.html
        x_new, y_new = splev(u_new, tck, der=0)
        # Convert it back to numpy format for opencv to be able to display it
        res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
        smoothened.append(np.asarray(res_array, dtype=np.int32))
    return(smoothened)

def find_red(image,fish,hue,sat,intensity):
    image_grey=cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    cimg = np.zeros_like(image_grey)

    cv2.drawContours(cimg, [fish], -1, 255, -1)
    pts = np.where(cimg == 255)

    img_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    list_intensities = []
    list_intensities.append(img_hsv[pts[0], pts[1]])

    img_empty = np.zeros(image_grey.shape, dtype=np.uint8)

    compteur_red = 0

    for inten in range(len(list_intensities[0])):
        if hue[0]>hue[1]:
            if (list_intensities[0][inten][0] <= hue[1] or list_intensities[0][inten][0] >= hue[0]) and list_intensities[0][inten][1] >= sat[0] and list_intensities[0][inten][1] <= sat[1] and list_intensities[0][inten][2] >= intensity[0] and list_intensities[0][inten][2] <= intensity[1]:
                compteur_red = compteur_red + 1
                img_empty[pts[0][inten], pts[1][inten]] = 255

        else:
            if (list_intensities[0][inten][0] >= hue[0] and list_intensities[0][inten][0] <= hue[1]) and list_intensities[0][inten][1] >= sat[0] and list_intensities[0][inten][1] <= sat[1] and list_intensities[0][inten][2] >= intensity[0] and list_intensities[0][inten][2] <= intensity[1]:
                compteur_red = compteur_red + 1
                img_empty[pts[0][inten], pts[1][inten]] = 255

    cnts2, _ = cv2.findContours(img_empty, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    return(cnts2)

def find_scale(image,hue,sat,intensity):
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    Binary_image = cv2.inRange(hsv, (hue[0], sat[0], intensity[0]), (hue[1], sat[1], intensity[1]))
    kernel = np.ones((7,7), np.uint8)
    Binary_image = cv2.dilate(Binary_image, kernel, iterations=7)
    Binary_image = cv2.erode(Binary_image, kernel, iterations=9)
    cnts,_=cv2.findContours(Binary_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    mask=np.zeros_like(Binary_image)

    if len(cnts) > 0:
        mask=cv2.drawContours(mask, cnts, -1, 255, -1)
        mask2=cv2.inRange(hsv, (0, 0, 225), (360, 255, 255))

        scale=cv2.bitwise_and(mask, mask2)
        cnts, _ = cv2.findContours(scale, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) > 0:
            cnts=sorted(cnts, key=cv2.contourArea, reverse=True)
            box= cv2.minAreaRect(cnts[0])
            points = cv2.boxPoints(box)

            pt1=[int((points[1][0]+points[2][0])/2), int((points[1][1]+points[2][1])/2)]
            pt2=[int((points[0][0]+points[3][0])/2), int((points[0][1]+points[3][1])/2)]
        else:
            pt1 = [50, 50]
            pt2 = [100, 50]
    else:
        pt1 = [50, 50]
        pt2 = [100, 50]

    return(pt1,pt2)

def color_calib(image, color):
    if color=="yellow":
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        Binary_image = cv2.inRange(hsv, (15, 50, 50), (35, 255, 255))
        kernel = np.ones((7,7), np.uint8)
        Binary_image = cv2.dilate(Binary_image, kernel, iterations=7)
        Binary_image = cv2.erode(Binary_image, kernel, iterations=25)
        cnts,_=cv2.findContours(Binary_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours=[]
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if area > 65000 and area < 260000:
                M = cv2.moments(cnt)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                if cY<1000 and cX<2000:
                    filtered_contours.append(cnt)
        if len(filtered_contours) > 0:
            cnt_ret = filtered_contours[0]
        else:
            cnt_ret = None


    elif color=="blue":
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        Binary_image = cv2.inRange(hsv, (90, 100, 100), (140, 255, 255))
        kernel = np.ones((7,7), np.uint8)
        Binary_image = cv2.dilate(Binary_image, kernel, iterations=7)
        Binary_image = cv2.erode(Binary_image, kernel, iterations=25)
        cnts,_=cv2.findContours(Binary_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) > 0:
            cnt_ret = cnts[len(cnts) - 1]
        else:
            cnt_ret = None


    elif color=="red":
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        Binary_image = cv2.inRange(hsv, (0, 50, 50), (15, 255, 255))
        kernel = np.ones((7,7), np.uint8)
        Binary_image = cv2.dilate(Binary_image, kernel, iterations=7)
        Binary_image = cv2.erode(Binary_image, kernel, iterations=25)
        cnts,_=cv2.findContours(Binary_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) > 0:
            cnt_ret = cnts[len(cnts) - 1]
        else:
            cnt_ret = None

    elif color=="white":
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        Binary_image = cv2.inRange(hsv, (0, 0, 125), (180, 15, 255))

        kernel = np.ones((7,7), np.uint8)
        Binary_image = cv2.dilate(Binary_image, kernel, iterations=7)
        Binary_image = cv2.erode(Binary_image, kernel, iterations=25)
        cnts,_=cv2.findContours(Binary_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours=[]
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if area > 65000 and area < 260000:
                M = cv2.moments(cnt)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                if cY<1000 and cX<2500:
                    filtered_contours.append(cnt)
        if len(filtered_contours)>0:
            cnt_ret=filtered_contours[0]
        else:
            cnt_ret = None

    return([cnt_ret])

