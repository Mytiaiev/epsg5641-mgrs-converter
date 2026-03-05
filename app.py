import tkinter as tk
from tkinter import ttk, messagebox
from pyproj import Transformer

<<<<<<< HEAD
# Украина, УСК-2000, зона 7: EPSG:5567 --> WGS84
transformer = Transformer.from_crs("EPSG:5567", "EPSG:4326", always_xy=True)

def convert_usk2000_zone7_to_wgs84(x, y):
    lon, lat = transformer.transform(x, y)
    return lat, lon
=======
# Преобразователь: EPSG:5641 -> WGS84
to_wgs = Transformer.from_crs("EPSG:5641", "EPSG:4326", always_xy=True)

# Сдвиги, вычисленные по 4 твоим парам (смотри объяснение выше)
DELTA_LAT = 0.00045
DELTA_LON = -0.00053

def convert_5641_to_corrected_wgs84(x, y):
    lon, lat = to_wgs.transform(x, y)
    lat_corr = lat - DELTA_LAT
    lon_corr = lon - DELTA_LON
    return lat_corr, lon_corr, lat, lon
>>>>>>> 4646498 (fix v2)

def do_convert():
    try:
        x = float(x_var.get().strip().replace(",", "."))
        y = float(y_var.get().strip().replace(",", "."))
    except ValueError:
        messagebox.showerror("Ошибка ввода", "Введите числа для X и Y.")
        return
    try:
<<<<<<< HEAD
        lat, lon = convert_usk2000_zone7_to_wgs84(x, y)
    except Exception as e:
        messagebox.showerror("Ошибка конвертации", str(e))
        return
=======
        latcorr, loncorr, lat, lon = convert_5641_to_corrected_wgs84(x, y)
    except Exception as e:
        messagebox.showerror("Ошибка конвертации", str(e))
        return
    latcorr_var.set(f"{latcorr:.8f}")
    loncorr_var.set(f"{loncorr:.8f}")
>>>>>>> 4646498 (fix v2)
    lat_var.set(f"{lat:.8f}")
    lon_var.set(f"{lon:.8f}")

root = tk.Tk()
<<<<<<< HEAD
root.title("УСК-2000 Зона 7 (EPSG:5567) → WGS84")

pad = {"padx": 10, "pady": 6}

ttk.Label(root, text="X (УСК-2000/зона 7)").grid(row=0, column=0, sticky="w", **pad)
x_var = tk.StringVar(value="13960918")
ttk.Entry(root, textvariable=x_var, width=20).grid(row=0, column=1, **pad)

ttk.Label(root, text="Y (УСК-2000/зона 7)").grid(row=1, column=0, sticky="w", **pad)
=======
root.title("EPSG:5641 → WGS84 (Google style)")

pad = {"padx": 10, "pady": 6}

ttk.Label(root, text="X (EPSG:5641)").grid(row=0, column=0, sticky="w", **pad)
x_var = tk.StringVar(value="13960918")
ttk.Entry(root, textvariable=x_var, width=20).grid(row=0, column=1, **pad)

ttk.Label(root, text="Y (EPSG:5641)").grid(row=1, column=0, sticky="w", **pad)
>>>>>>> 4646498 (fix v2)
y_var = tk.StringVar(value="16149503")
ttk.Entry(root, textvariable=y_var, width=20).grid(row=1, column=1, **pad)

ttk.Button(root, text="Конвертировать", command=do_convert).grid(row=2, columnspan=2, **pad)

ttk.Separator(root).grid(row=3, column=0, columnspan=2, sticky="ew", **pad)

<<<<<<< HEAD
ttk.Label(root, text="Широта (lat)").grid(row=4, column=0, sticky="w", **pad)
lat_var = tk.StringVar()
ttk.Entry(root, textvariable=lat_var, width=25, state="readonly").grid(row=4, column=1, **pad)

ttk.Label(root, text="Долгота (lon)").grid(row=5, column=0, sticky="w", **pad)
lon_var = tk.StringVar()
ttk.Entry(root, textvariable=lon_var, width=25, state="readonly").grid(row=5, column=1, **pad)
=======
ttk.Label(root, text="lat_corr (точно как нужно)").grid(row=4, column=0, sticky="w", **pad)
latcorr_var = tk.StringVar()
ttk.Entry(root, textvariable=latcorr_var, width=25, state="readonly").grid(row=4, column=1, **pad)

ttk.Label(root, text="lon_corr (точно как нужно)").grid(row=5, column=0, sticky="w", **pad)
loncorr_var = tk.StringVar()
ttk.Entry(root, textvariable=loncorr_var, width=25, state="readonly").grid(row=5, column=1, **pad)

ttk.Label(root, text="lat_pyproj (ориг.)").grid(row=6, column=0, sticky="w", **pad)
lat_var = tk.StringVar()
ttk.Entry(root, textvariable=lat_var, width=25, state="readonly").grid(row=6, column=1, **pad)

ttk.Label(root, text="lon_pyproj (ориг.)").grid(row=7, column=0, sticky="w", **pad)
lon_var = tk.StringVar()
ttk.Entry(root, textvariable=lon_var, width=25, state="readonly").grid(row=7, column=1, **pad)
>>>>>>> 4646498 (fix v2)

root.bind("<Return>", lambda _: do_convert())
root.mainloop()