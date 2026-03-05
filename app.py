import tkinter as tk
from tkinter import ttk, messagebox

from pyproj import Transformer

# EPSG:5641 -> WGS84
TO_WGS84 = Transformer.from_crs("EPSG:5641", "EPSG:4326", always_xy=True)

# WGS84 -> UTM zone 37N (EPSG:32637)
TO_UTM37 = Transformer.from_crs("EPSG:4326", "EPSG:32637", always_xy=True)

FIXED_GZD = "37U"
FIXED_100K = "CP"

def convert():
    try:
        x = float(x_var.get().strip().replace(",", "."))
        y = float(y_var.get().strip().replace(",", "."))
    except Exception:
        messagebox.showerror("Ошибка", "Введите корректные числа X и Y (EPSG:5641).")
        return

    try:
        lon, lat = TO_WGS84.transform(x, y)
        e_utm, n_utm = TO_UTM37.transform(lon, lat)

        # цифры внутри 100км квадрата
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
root.title("EPSG:5641 → 37U CP (offline)")
root.resizable(False, False)

pad = {"padx": 10, "pady": 6}

frm = ttk.Frame(root)
frm.grid(row=0, column=0, sticky="nsew")

ttk.Label(frm, text="X (EPSG:5641)").grid(row=0, column=0, sticky="w", **pad)
x_var = tk.StringVar(value="13956567")
ttk.Entry(frm, textvariable=x_var, width=28).grid(row=0, column=1, **pad)

ttk.Label(frm, text="Y (EPSG:5641)").grid(row=1, column=0, sticky="w", **pad)
y_var = tk.StringVar(value="16137863")
ttk.Entry(frm, textvariable=y_var, width=28).grid(row=1, column=1, **pad)

btns = ttk.Frame(frm)
btns.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=8)
ttk.Button(btns, text="Convert", command=convert).grid(row=0, column=0, padx=5)
ttk.Button(btns, text="Copy", command=copy_mgrs).grid(row=0, column=1, padx=5)

ttk.Separator(frm).grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=8)

ttk.Label(frm, text="MGRS (fixed 37U CP)").grid(row=4, column=0, sticky="w", **pad)
mgrs_var = tk.StringVar()
ttk.Entry(frm, textvariable=mgrs_var, width=34, state="readonly").grid(row=4, column=1, **pad)

ttk.Label(frm, text="UTM 37N (E,N)").grid(row=5, column=0, sticky="w", **pad)
utm_var = tk.StringVar()
ttk.Entry(frm, textvariable=utm_var, width=34, state="readonly").grid(row=5, column=1, **pad)

ttk.Label(frm, text="Lat (WGS84)").grid(row=6, column=0, sticky="w", **pad)
lat_var = tk.StringVar()
ttk.Entry(frm, textvariable=lat_var, width=34, state="readonly").grid(row=6, column=1, **pad)

ttk.Label(frm, text="Lon (WGS84)").grid(row=7, column=0, sticky="w", **pad)
lon_var = tk.StringVar()
ttk.Entry(frm, textvariable=lon_var, width=34, state="readonly").grid(row=7, column=1, **pad)

root.bind("<Return>", lambda e: convert())
root.mainloop()