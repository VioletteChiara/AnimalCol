import numpy as np
import cv2


def create_sat_val(hue, sb, st, vb, vt):
    sat_range = np.arange(sb, st + 1, dtype=np.uint8)  # X-axis (width)
    val_range = np.arange(vb, vt + 1, dtype=np.uint8)  # Y-axis (height)

    H = len(val_range)
    W = len(sat_range)

    # Fixed hue (just use hb for now)
    Hu = np.full((H, W), int(hue/2), dtype=np.uint8)

    # Gradient grids
    Sa = np.tile(sat_range, (H, 1))  # shape: (H, W)
    Va = np.tile(val_range[:, np.newaxis], (1, W))  # shape: (H, W)

    # Stack HSV and convert to BGR
    hsv = np.stack((Hu, Sa, Va), axis=2)  # shape: (H, W, 3)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    return bgr

def create_hue(hb, ht):
    if hb<0:
        hb=360-hb

    if ht<0:
        ht=360-ht

    if hb>ht:
        hue_range_high = np.arange(int(hb / 2), 179 + 1, dtype=np.uint8)  # X-axis (width)
        hue_range_low = np.arange(0, int(ht / 2) + 1, dtype=np.uint8)  # X-axis (width)
        hue_range =np.concatenate([hue_range_high, hue_range_low], axis=0)
    else:
        hue_range = np.arange(int(hb/2), int(ht/2) + 1, dtype=np.uint8)  # X-axis (width)
    H = len(hue_range)
    W=20
    # Fixed hue (just use hb for now)
    Hu = np.tile(hue_range[:, np.newaxis], (1, W))

    # Gradient grids
    Sa = np.full((H, W), 255, dtype=np.uint8)
    Va = np.full((H, W), 255, dtype=np.uint8)

    # Stack HSV and convert to BGR
    hsv = np.stack((Hu, Sa, Va), axis=2)  # shape: (H, W, 3)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    return bgr


def create_all_sat():
    sat_range = np.arange(0, 255 + 1, dtype=np.uint8)  # X-axis (width)
    H = len(sat_range)
    W = 20
    # Fixed hue (just use hb for now)
    Sa = np.tile(sat_range[:, np.newaxis], (1, W))

    # Gradient grids
    Hu = np.full((H, W), 0, dtype=np.uint8)
    Va = np.full((H, W), 255, dtype=np.uint8)

    # Stack HSV and convert to BGR
    hsv = np.stack((Hu, Sa, Va), axis=2)  # shape: (H, W, 3)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    return bgr

def create_all_val():
    val_range = np.arange(0, 255 + 1, dtype=np.uint8)  # X-axis (width)
    H = len(val_range)
    W = 20
    # Fixed hue (just use hb for now)
    Va = np.tile(val_range[:, np.newaxis], (1, W))

    # Gradient grids
    Hu = np.full((H, W), 0, dtype=np.uint8)
    Sa = np.full((H, W), 0, dtype=np.uint8)

    # Stack HSV and convert to BGR
    hsv = np.stack((Hu, Sa, Va), axis=2)  # shape: (H, W, 3)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    return bgr