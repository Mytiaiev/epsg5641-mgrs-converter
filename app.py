import csv
import math
import os
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from pyproj import Transformer

# WGS84 -> UTM zone 37N
TO_UTM37 = Transformer.from_crs("EPSG:4326", "EPSG:32637", always_xy=True)

FIXED_GZD = "37U"
FIXED_100K = "CP"

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CALIBRATION_CSV = os.path.join(APP_DIR, "calibration_points.csv")

def load_points(path: str):
    pts = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            x = float(row["x"])
            y = float(row["y"])
            lat = float(row["lat"])
            lon = float(row["lon"])
            pts.append((x, y, lat, lon))
    if len(pts) < 3:
        raise ValueError("Нужно минимум 3 точки в calibration_points.csv")
    return pts

def fit_affine_xy_to_latlon(points):
    """
    lat = a1*x + a2*y + a0
    lon = b1*x + b2*y + b0
    """
    A = []
    latv = []
    lonv = []
    for x, y, lat, lon in points:
        A.append([x, y, 1.0])
        latv.append(lat)
        lonv.append(lon)
    A = np.array(A, dtype=float)
    latv = np.array(latv, dtype=float)
    lonv = np.array(lonv, dtype=float)

    a, *_ = np.linalg.lstsq(A, latv, rcond=None)  # [a1,a2,a0]
    b, *_ = np.linalg.lstsq(A, lonv, rcond=None)  # [b1,b2,b0]
    return a, b

def predict_latlon(a, b, x, y):
    lat = a[0]*x + a[1]*y + a[2]
    lon = b[0]*x + b[1]*y + b[2]
    return float(lat), float(lon)

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1 = math.radians(lat1); p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2*R*math.asin(math.sqrt(a))

def calibration_report(points, a, b):
    errs = []
    for x, y, lat, lon in points:
        lat2, lon2 = predict_latlon(a, b, x, y)
        errs.append(haversine_m(lat, lon, lat2, lon2))
    rmse = (sum(e*e for e in errs) / len(errs)) ** 0.5
    return rmse, max(errs)

try:
    _points = load_points(CALIBRATION_CSV)
    _a, _b = fit_affine_xy_to_latlon(_points)
    _rmse_m, _max_m = calibration_report(_points, _a, _b)
    _calib_ok = True
except Exception as e:
    _points = []
    _a = _b = None
    _rmse_m = _max_m = None
    _calib_ok = False
    _calib_error = str(e)

def convert():
    if not _calib_ok:
        messagebox.showerror(
            "Калибровка не загружена",
            f"Не удалось прочитать/подогнать calibration_points.csv:\n{_calib_error}"
        )
        return

    try:
        x = float(x_var.get().strip().replace(",", "."))
        y = float(y_var.get().strip().replace(",", "."))
    except Exception:
        messagebox.showerror("Ошибка", "Введите корректные числа X и Y (из Alpine Quest).")
        return

    try:
        lat, lon = predict_latlon(_a, _b, x, y)
        e_utm, n_utm = TO_UTM37.transform(lon, lat)

        e5 = int(round(e_utm)) % 100000
        n5 = int(round(n_utm)) % 100000

        mgrs_str = f"{FIXED_GZD} {FIXED_100K} {e5:05d} {n5:05d}"

        mgrs_var.set(mgrs_str)
        utm_var.set(f"{e_utm:.3f}, {n_utm:.3f}")
        lat_var.set(f"{lat:.8f}")
        lon_var.set(f"{lon:.8f}")

    except Exception as e:
        messagebox.showerror("Ошибка конвертации", str(e))

def copy_mgrs():
    s = mgrs_var.get()
    if not s:
        return
    root.clipboard_clear()
    root.clipboard_append(s)

root = tk.Tk()
root.title("AQ Brazil Mercator → 37U CP (calibrated)")
root.resizable(False, False)

pad = {"padx": 10, "pady": 6}

frm = ttk.Frame(root)
frm.grid(row=0, column=0, sticky="nsew")

# Status
if _calib_ok:
    status_text = f"Calib OK | points={len(_points)} | RMSE≈{_rmse_m:.1f} m | max≈{_max_m:.1f} m"
else:
    status_text = f"Calib ERROR: {_calib_error}"
ttk.Label(frm, text=status_text).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))

ttk.Label(frm, text="X (AQ Brazil Mercator)").grid(row=1, column=0, sticky="w", **pad)
x_var = tk.StringVar(value="13950085")
ttk.Entry(frm, textvariable=x_var, width=30).grid(row=1, column=1, **pad)

ttk.Label(frm, text="Y (AQ Brazil Mercator)").grid(row=2, column=0, sticky="w", **pad)
y_var = tk.StringVar(value="16156045")
ttk.Entry(frm, textvariable=y_var, width=30).grid(row=2, column=1, **pad)

btns = ttk.Frame(frm)
btns.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=8)
ttk.Button(btns, text="Convert", command=convert).grid(row=0, column=0, padx=5)
ttk.Button(btns, text="Copy", command=copy_mgrs).grid(row=0, column=1, padx=5)

ttk.Separator(frm).grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=8)

ttk.Label(frm, text="MGRS (fixed 37U CP)").grid(row=5, column=0, sticky="w", **pad)
mgrs_var = tk.StringVar()
ttk.Entry(frm, textvariable=mgrs_var, width=38, state="readonly").grid(row=5, column=1, **pad)

ttk.Label(frm, text="UTM 37N (E,N)").grid(row=6, column=0, sticky="w", **pad)
utm_var = tk.StringVar()
ttk.Entry(frm, textvariable=utm_var, width=38, state="readonly").grid(row=6, column=1, **pad)

ttk.Label(frm, text="Lat (WGS84)").grid(row=7, column=0, sticky="w", **pad)
lat_var = tk.StringVar()
ttk.Entry(frm, textvariable=lat_var, width=38, state="readonly").grid(row=7, column=1, **pad)

ttk.Label(frm, text="Lon (WGS84)").grid(row=8, column=0, sticky="w", **pad)
lon_var = tk.StringVar()
ttk.Entry(frm, textvariable=lon_var, width=38, state="readonly").grid(row=8, column=1, **pad)

root.bind("<Return>", lambda e: convert())
root.mainloop()