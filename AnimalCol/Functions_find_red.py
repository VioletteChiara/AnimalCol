import cv2
import numpy as np

def find_particles(image,contours,target,hue,sat,val,ero,dil):
    if not target is None:
        image_grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        target_mask = np.zeros_like(image_grey)

        if not contours[0] is None and not contours[0][0] is None:
            cv2.drawContours(target_mask, contours[0], target, 255, -1, hierarchy=contours[1])
            img_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

            if hue[0] < hue[1]:
                mask=cv2.inRange(img_hsv,np.array([hue[0],sat[0],val[0]]),np.array([hue[1],sat[1],val[1]]))
            else:
                mask_low = cv2.inRange(img_hsv, np.array([hue[0], sat[0], val[0]]), np.array([180, sat[1], val[1]]))
                mask_high = cv2.inRange(img_hsv, np.array([0, sat[0], val[0]]), np.array([hue[1], sat[1], val[1]]))
                mask = cv2.bitwise_or(mask_low, mask_high)

            if ero>0:
                kernel = np.ones((3,3), np.uint8)
                mask=cv2.erode(mask,kernel,iterations=ero)
            if dil>0:
                kernel = np.ones((3, 3), np.uint8)
                mask = cv2.dilate(mask, kernel,iterations=dil)

            final_mask=cv2.bitwise_and(mask, target_mask)

            cnts2, hierarchy = cv2.findContours(final_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            return(cnts2, hierarchy)

    return([[],[]])


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

