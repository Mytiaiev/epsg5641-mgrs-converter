import tkinter as tk
from tkinter import ttk, messagebox

from pyproj import Transformer
import mgrs

_TO_WGS84 = Transformer.from_crs("EPSG:5641", "EPSG:4326", always_xy=True)
_M = mgrs.MGRS()

def pretty_mgrs(s: str, precision: int) -> str:
    i = 0
    while i < len(s) and s[i].isdigit():
        i += 1
    zone = s[:i]
    band = s[i:i+1]
    grid = s[i+1:i+3]
    rest = s[i+3:]
    half = len(rest) // 2
    e = rest[:half]
    n = rest[half:]
    return f"{zone}{band} {grid} {e} {n}"

def convert():
    try:
        x = float(x_var.get().strip().replace(",", "."))
        y = float(y_var.get().strip().replace(",", "."))
    except Exception:
        messagebox.showerror("Ошибка", "Введите корректные числа X и Y.")
        return

    try:
        lon, lat = _TO_WGS84.transform(x, y)
        prec = int(precision_var.get())
        raw = _M.toMGRS(lat, lon, MGRSPrecision=prec).decode("ascii")
        out = pretty_mgrs(raw, prec)
    except Exception as e:
        messagebox.showerror("Ошибка конвертации", str(e))
        return

    mgrs_var.set(out)
    lat_var.set(f"{lat:.8f}")
    lon_var.set(f"{lon:.8f}")

def copy_mgrs():
    s = mgrs_var.get()
    if not s:
        return
    root.clipboard_clear()
    root.clipboard_append(s)

root = tk.Tk()
root.title("EPSG:5641 → MGRS (offline)")
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

ttk.Label(frm, text="MGRS precision").grid(row=2, column=0, sticky="w", **pad)
precision_var = tk.StringVar(value="5")
ttk.Combobox(frm, textvariable=precision_var, values=["0","1","2","3","4","5"], width=25, state="readonly").grid(row=2, column=1, **pad)

btns = ttk.Frame(frm)
btns.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=8)
ttk.Button(btns, text="Convert", command=convert).grid(row=0, column=0, padx=5)
ttk.Button(btns, text="Copy MGRS", command=copy_mgrs).grid(row=0, column=1, padx=5)

ttk.Separator(frm).grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=8)

ttk.Label(frm, text="MGRS").grid(row=5, column=0, sticky="w", **pad)
mgrs_var = tk.StringVar()
ttk.Entry(frm, textvariable=mgrs_var, width=28, state="readonly").grid(row=5, column=1, **pad)

ttk.Label(frm, text="Lat (WGS84)").grid(row=6, column=0, sticky="w", **pad)
lat_var = tk.StringVar()
ttk.Entry(frm, textvariable=lat_var, width=28, state="readonly").grid(row=6, column=1, **pad)

ttk.Label(frm, text="Lon (WGS84)").grid(row=7, column=0, sticky="w", **pad)
lon_var = tk.StringVar()
ttk.Entry(frm, textvariable=lon_var, width=28, state="readonly").grid(row=7, column=1, **pad)

root.bind("<Return>", lambda e: convert())
root.mainloop()