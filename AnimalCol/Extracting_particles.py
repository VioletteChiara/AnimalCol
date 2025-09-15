from tkinter import filedialog
import numpy as np
import cv2
import math
import csv
from scipy.stats import circmean
import pickle
import os

import AnimalCol.Loading as Loading
import AnimalCol.User_loading as User_loading

def save_particles(load_frame, Datas_generales, distance, Images):
    # Loading of the parameters that must remain always, independently from the projects (for now, only auto update exists)
    Param_file = User_loading.resource_path(os.path.join("Settings"))
    with open(Param_file, 'rb') as fp:
        Params_settings = pickle.load(fp)
    export_particles=Params_settings["Export_particles"]

    load_frame = Loading.Loading(load_frame)  # Progression bar
    load_frame.show_load(0)
    file_to_save = filedialog.asksaveasfilename(defaultextension=".csv")
    with open(file_to_save, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        Names = ["File", "Type", "Target_ID", "ID", "Area", "Mean_Hue", "Mean_Saturation", "Mean_Value","Length","Width"]
        writer.writerow(Names)

        for i in range(len(Datas_generales)):
            current_pos = i / len(Datas_generales)
            load_frame.show_load(current_pos)
            Vid_loading_len=(1/len(Datas_generales))

            ratio_mm = float(distance.get()) / math.sqrt(
                (Datas_generales[i]["Scale"][0][0] - Datas_generales[i]["Scale"][1][0]) ** 2 + (
                        Datas_generales[i]["Scale"][0][1] - Datas_generales[i]["Scale"][1][1]) ** 2)

            target=0
            if not Datas_generales[i]["Target"][1] is None:
                for j in range(len(Datas_generales[i]["Target"][1][0])):
                    if Datas_generales[i]["Target"][1][0][j][3]==-1:
                        current_pos=j/len(Datas_generales[i]["Target"][1][0])*Vid_loading_len+current_pos
                        Target_loading_len=(1/len(Datas_generales[i]["Target"][1][0])*Vid_loading_len)
                        load_frame.show_load(current_pos)
                        File = Datas_generales[i]["File"]
                        Type = "Target"
                        Fish_ID = target

                        Area_mm, Mean_H, Mean_S, Mean_V, w,h = extract_data(Images[i], Datas_generales[i]["Target"], j, ratio_mm)

                        raw = [File, Type, Fish_ID, "NA", Area_mm, Mean_H, Mean_S, Mean_V, w,h]
                        writer.writerow(raw)

                        # We calcualte the average hsv of all particles
                        Type = "All_particles"
                        if len(Datas_generales[i]["Particles"]) and len(Datas_generales[i]["Particles"][target])>0:
                            Area_mm, Mean_H, Mean_S, Mean_V, w,h = extract_data(Images[i], Datas_generales[i]["Particles"][target], -1, ratio_mm)
                            raw = [File, Type, Fish_ID, "NA", Area_mm, Mean_H, Mean_S, Mean_V, "NA","NA"]
                            writer.writerow(raw)

                            load_frame.show_load(
                                (i + target / len(Datas_generales[i]["Particles"])) / len(Datas_generales))
                            if export_particles:
                                for k in range(len(Datas_generales[i]["Particles"][target][0])):
                                    load_frame.show_load((k/len(Datas_generales[i]["Particles"][target][0])) * Target_loading_len +current_pos)
                                    if Datas_generales[i]["Particles"][target][1][0][k][3] == -1:
                                        File = Datas_generales[i]["File"]
                                        Type = "Particle"
                                        Fish_ID = target
                                        ID = k
                                        Area_mm, Mean_H, Mean_S, Mean_V, w,h = extract_data(Images[i], Datas_generales[i]["Particles"][target], k, ratio_mm)
                                        raw = [File, Type, Fish_ID, ID, Area_mm, Mean_H, Mean_S, Mean_V, "NA","NA"]
                                        writer.writerow(raw)

                            target += 1
                    else:
                        raw = [File, Type, Fish_ID, 0, "NA", "NA", "NA", "NA", "NA", "NA"]
                        writer.writerow(raw)

            for color in ["Yellow", "Blue", "Red", "White"]:
                if len(Datas_generales[i][color])>0:
                    for j in range(len(Datas_generales[i][color][1][0])):
                        if Datas_generales[i][color][1][0][j][3] == -1:
                            File = Datas_generales[i]["File"]
                            Type = color
                            ID = j
                            Area_mm, Mean_H, Mean_S, Mean_V, w, h = extract_data(Images[i],
                                                                              Datas_generales[i][color],
                                                                              j, ratio_mm)

                            raw = [File, Type, "NA", ID, Area_mm, Mean_H, Mean_S, Mean_V, w, h]
                            writer.writerow(raw)


    load_frame.destroy()



def extract_data(image, contours, id,ratio_mm):
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mask = np.zeros(grey.shape, dtype=np.uint8)
    mask = cv2.drawContours(mask, contours[0], id, (255, 255, 255), -1, hierarchy=contours[1])

    if id>=0:
        (center), (w, h), angle = cv2.minAreaRect(contours[0][id])
        w = max(w, h)
        h = min(w, h)

        w = w * ratio_mm
        h = h * ratio_mm

    else:
        w="NA"
        h="NA"

    ret, mask = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
    _, Mean_S, Mean_V, _ = cv2.mean(hsv, mask)

    # We calculate the mean hue ourselves to avoid problem with circularity (0-360 hue values)
    hues = hsv[:, :, 0]
    hues_values = hues[mask > 0]
    Area = len(hues_values)
    Area_mm = Area * (ratio_mm ** 2)

    Mean_H = circmean(hues_values, high=180, low=0)
    Mean_H=Mean_H*2

    if Area == 0:
        Mean_S = "NA"
        Mean_V = "NA"
        Mean_H ="NA"


    return(Area_mm, Mean_H, Mean_S, Mean_V, w,h )

