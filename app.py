import tkinter as tk
from tkinter import ttk, messagebox
from pyproj import Transformer

# Украина, УСК-2000, зона 7: EPSG:5567 --> WGS84
transformer = Transformer.from_crs("EPSG:5567", "EPSG:4326", always_xy=True)

def convert_usk2000_zone7_to_wgs84(x, y):
    lon, lat = transformer.transform(x, y)
    return lat, lon

def do_convert():
    try:
        x = float(x_var.get().strip().replace(",", "."))
        y = float(y_var.get().strip().replace(",", "."))
    except ValueError:
        messagebox.showerror("Ошибка ввода", "Введите числа для X и Y.")
        return
    try:
        lat, lon = convert_usk2000_zone7_to_wgs84(x, y)
    except Exception as e:
        messagebox.showerror("Ошибка конвертации", str(e))
        return
    lat_var.set(f"{lat:.8f}")
    lon_var.set(f"{lon:.8f}")

root = tk.Tk()
root.title("УСК-2000 Зона 7 (EPSG:5567) → WGS84")

pad = {"padx": 10, "pady": 6}

ttk.Label(root, text="X (УСК-2000/зона 7)").grid(row=0, column=0, sticky="w", **pad)
x_var = tk.StringVar(value="13960918")
ttk.Entry(root, textvariable=x_var, width=20).grid(row=0, column=1, **pad)

ttk.Label(root, text="Y (УСК-2000/зона 7)").grid(row=1, column=0, sticky="w", **pad)
y_var = tk.StringVar(value="16149503")
ttk.Entry(root, textvariable=y_var, width=20).grid(row=1, column=1, **pad)

ttk.Button(root, text="Конвертировать", command=do_convert).grid(row=2, columnspan=2, **pad)

ttk.Separator(root).grid(row=3, column=0, columnspan=2, sticky="ew", **pad)

ttk.Label(root, text="Широта (lat)").grid(row=4, column=0, sticky="w", **pad)
lat_var = tk.StringVar()
ttk.Entry(root, textvariable=lat_var, width=25, state="readonly").grid(row=4, column=1, **pad)

ttk.Label(root, text="Долгота (lon)").grid(row=5, column=0, sticky="w", **pad)
lon_var = tk.StringVar()
ttk.Entry(root, textvariable=lon_var, width=25, state="readonly").grid(row=5, column=1, **pad)

root.bind("<Return>", lambda _: do_convert())
root.mainloop()