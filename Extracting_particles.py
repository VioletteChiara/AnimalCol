from tkinter import filedialog
import numpy as np
import cv2
import math
import csv
import Loading
from scipy.stats import circmean


def save_particles(load_frame, Datas_generales, distance, Images):
    load_frame = Loading.Loading(load_frame)  # Progression bar
    load_frame.show_load(0)
    file_to_save = filedialog.asksaveasfilename(defaultextension=".csv")
    with open(file_to_save, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        Names = ["File", "Type", "Target_ID", "ID", "Area", "Mean_Hue", "Mean_Saturation", "Mean_Value"]
        writer.writerow(Names)

        for i in range(len(Datas_generales)):
            load_frame.show_load(i / len(Datas_generales))
            ratio_mm = float(distance.get()) / math.sqrt(
                (Datas_generales[i]["Scale"][0][0] - Datas_generales[i]["Scale"][1][0]) ** 2 + (
                        Datas_generales[i]["Scale"][0][1] - Datas_generales[i]["Scale"][1][1]) ** 2)

            target=0
            for j in range(len(Datas_generales[i]["Target"][0])):
                if Datas_generales[i]["Target"][1][0][j][3]==-1:
                    File = Datas_generales[i]["File"]
                    Type = "Target"
                    Fish_ID = target
                    ID = target
                    hsv = cv2.cvtColor(Images[i], cv2.COLOR_RGB2HSV)
                    grey = cv2.cvtColor(Images[i], cv2.COLOR_RGB2GRAY)
                    mask = np.zeros(grey.shape, dtype=np.uint8)
                    mask = cv2.drawContours(mask, Datas_generales[i]["Target"][0], j, (255, 255, 255), -1, hierarchy=Datas_generales[i]["Target"][1])
                    ret, mask = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
                    _, Mean_S, Mean_V, _ = cv2.mean(hsv, mask)

                    # We calculate the mean hue ourselves to avoid problem with circularity (0-360 hue values)
                    hues = hsv[:, :, 0]
                    hues_values = hues[mask > 0]
                    Area=len(hues_values)
                    Area_mm = Area * (ratio_mm ** 2)
                    Mean_H = circmean(hues_values, high=180, low=0)
                    raw = [File, Type, Fish_ID, ID, Area_mm, Mean_H * 2, Mean_S, Mean_V]
                    writer.writerow(raw)

                    # We calcualte the average hsv of all particles
                    Type = "All_particles"
                    particles=Datas_generales[i]["Particles"][target][0]
                    mask = np.zeros(grey.shape, dtype=np.uint8)
                    mask_parts = cv2.drawContours(mask, particles, -1, (255, 255, 255), -1)
                    ret, mask_parts = cv2.threshold(mask_parts, 50, 255, cv2.THRESH_BINARY)
                    _, Mean_S, Mean_V, _ = cv2.mean(hsv, mask_parts)
                    # We calculate the mean hue ourselves to avoid problem with circularity (0-360 hue values)
                    hues = hsv[:, :, 0]
                    hues_values = hues[mask_parts > 0]
                    Mean_H = circmean(hues_values, high=180, low=0)
                    Area=len(hues_values)
                    Area_mm = Area * (ratio_mm ** 2)

                    if Area==0:
                        Mean_S=np.nan
                        Mean_V=np.nan

                    raw = [File, Type, Fish_ID, ID, Area_mm, Mean_H * 2, Mean_S, Mean_V]
                    writer.writerow(raw)

                    load_frame.show_load(
                        (i + target / len(Datas_generales[i]["Particles"])) / len(Datas_generales))
                    for k in range(len(Datas_generales[i]["Particles"][target][0])):
                        if Datas_generales[i]["Particles"][target][1][0][k][3] == -1:
                            File = Datas_generales[i]["File"]
                            Type = "Particle"
                            Fish_ID = target
                            ID = k

                            hsv = cv2.cvtColor(Images[i], cv2.COLOR_RGB2HSV)
                            grey = cv2.cvtColor(Images[i], cv2.COLOR_RGB2GRAY)
                            mask = np.zeros(grey.shape, dtype=np.uint8)
                            mask = cv2.drawContours(mask, Datas_generales[i]["Particles"][target][0], k, (255, 255, 255), -1, hierarchy=Datas_generales[i]["Particles"][target][1])
                            ret, mask = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
                            _, Mean_S, Mean_V, _ = cv2.mean(hsv, mask)


                            # We calculate the mean hue ourselves to avoid problem with circularity (0-360 hue values)
                            hues = hsv[:, :, 0]
                            hues_values = hues[mask > 0]
                            Area = len(hues_values)
                            Area_mm = Area * (ratio_mm ** 2)
                            Mean_H = circmean(hues_values, high=180, low=0)
                            raw = [File, Type, Fish_ID, ID, Area_mm, Mean_H * 2, Mean_S, Mean_V]
                            writer.writerow(raw)
                    target += 1

            for color in ["Yellow", "Blue", "Red", "White"]:
                for j in range(len(Datas_generales[i][color])):
                    if not (Datas_generales[i][color][j] is None):
                        File = Datas_generales[i]["File"]
                        Type = color
                        ID = j
                        Area = cv2.contourArea(Datas_generales[i][color][j])
                        Area_mm = Area * (ratio_mm ** 2)
                        hsv = cv2.cvtColor(Images[i], cv2.COLOR_RGB2HSV)
                        grey = cv2.cvtColor(Images[i], cv2.COLOR_RGB2GRAY)
                        mask = np.zeros(grey.shape, dtype=np.uint8)
                        mask = cv2.drawContours(mask, [Datas_generales[i][color][j]], -1, (255, 255, 255), -1)
                        ret, mask = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
                        _, Mean_S, Mean_V, _ = cv2.mean(hsv, mask)
                        # We calculate the mean hue ourselves to avoid problem with circularity (0-360 hue values)
                        hues = hsv[:, :, 0]
                        hues_values = hues[mask > 0]
                        Mean_H = circmean(hues_values, high=180, low=0)
                        raw = [File, Type, "NA", ID, Area_mm, Mean_H * 2, Mean_S, Mean_V]
                        writer.writerow(raw)

    load_frame.destroy()



def get_net_contour_area(index, contours, hierarchy):
    net_area = cv2.contourArea(contours[index])
    child = hierarchy[0][index][2]  # First child
    while child != -1:
        net_area -= cv2.contourArea(contours[child])
        child = hierarchy[0][child][0]  # Next sibling (another hole)
    return net_area