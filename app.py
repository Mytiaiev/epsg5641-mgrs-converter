import os
import sys

# Fix for PyInstaller: ensure mgrs can find its native library
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    try:
        base_path = sys._MEIPASS
        mgrs_dir = os.path.join(base_path, "mgrs")
        if os.path.isdir(mgrs_dir):
            os.environ["PATH"] = mgrs_dir + os.pathsep + os.environ.get("PATH", "")
            if mgrs_dir not in sys.path:
                sys.path.insert(0, mgrs_dir)
    except AttributeError:
        pass

import tkinter as tk
from tkinter import ttk, messagebox

from pyproj import Transformer
import mgrs as mgrs_lib

# EPSG:5641 (SIRGAS 2000 / Brazil Mercator) -> WGS84
_transformer = Transformer.from_crs("EPSG:5641", "EPSG:4326", always_xy=True)
_mgrs = mgrs_lib.MGRS()


def convert_5641_to_mgrs(x, y, mgrs_precision=5):
    """
    x, y — EPSG:5641 coordinates (SIRGAS 2000 / Brazil Mercator)
    Returns: (mgrs_string, lat, lon)
    """
    lon, lat = _transformer.transform(x, y)
    mgrs_string = _mgrs.toMGRS(lat, lon, MGRSPrecision=mgrs_precision)
    return mgrs_string, lat, lon


def do_convert():
    try:
        x = float(x_var.get().strip().replace(",", "."))
        y = float(y_var.get().strip().replace(",", "."))
    except ValueError:
        messagebox.showerror("Input error", "Enter valid numbers for X and Y.")
        return

    precision = precision_var.get()

    try:
        mgrs_string, lat, lon = convert_5641_to_mgrs(x, y, mgrs_precision=precision)
    except Exception as e:
        messagebox.showerror("Conversion error", str(e))
        return

    mgrs_var.set(mgrs_string)
    lat_var.set(f"{lat:.8f}")
    lon_var.set(f"{lon:.8f}")


def copy_mgrs():
    s = mgrs_var.get()
    if s:
        root.clipboard_clear()
        root.clipboard_append(s)


def do_batch():
    raw = batch_text.get("1.0", tk.END).strip()
    if not raw:
        messagebox.showinfo("Batch", "Paste X Y pairs into the text area first.")
        return

    precision = precision_var.get()
    results = []
    errors = []

    for i, line in enumerate(raw.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        parts = line.replace(",", ".").split()
        if len(parts) < 2:
            errors.append(f"Line {i}: cannot parse '{line}'")
            continue
        try:
            x, y = float(parts[0]), float(parts[1])
        except ValueError:
            errors.append(f"Line {i}: cannot parse '{line}'")
            continue
        try:
            mgrs_string, lat, lon = convert_5641_to_mgrs(x, y, mgrs_precision=precision)
            results.append(f"{x:.0f}\t{y:.0f}\t{mgrs_string}\t{lat:.8f}\t{lon:.8f}")
        except Exception as e:
            errors.append(f"Line {i}: {e}")

    batch_result.config(state="normal")
    batch_result.delete("1.0", tk.END)
    if results:
        header = "X\tY\tMGRS\tLat\tLon\n"
        batch_result.insert(tk.END, header + "\n".join(results))
    if errors:
        batch_result.insert(tk.END, "\n\nErrors:\n" + "\n".join(errors))
    batch_result.config(state="disabled")


# ── UI ─────────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("EPSG:5641 → MGRS Converter")
root.resizable(False, False)

nb = ttk.Notebook(root)
nb.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

# ── Single conversion tab ──────────────────────────────────────────────────────
tab_single = ttk.Frame(nb)
nb.add(tab_single, text="Single")

pad = {"padx": 10, "pady": 6}

ttk.Label(tab_single, text="X (EPSG:5641)").grid(row=0, column=0, sticky="w", **pad)
x_var = tk.StringVar(value="13950085")
ttk.Entry(tab_single, textvariable=x_var, width=30).grid(row=0, column=1, **pad)

ttk.Label(tab_single, text="Y (EPSG:5641)").grid(row=1, column=0, sticky="w", **pad)
y_var = tk.StringVar(value="16156045")
ttk.Entry(tab_single, textvariable=y_var, width=30).grid(row=1, column=1, **pad)

ttk.Label(tab_single, text="Precision (1–5)").grid(row=2, column=0, sticky="w", **pad)
precision_var = tk.IntVar(value=5)
ttk.Spinbox(tab_single, from_=1, to=5, textvariable=precision_var, width=5).grid(
    row=2, column=1, sticky="w", **pad
)

btns = ttk.Frame(tab_single)
btns.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=8)
ttk.Button(btns, text="Convert", command=do_convert).grid(row=0, column=0, padx=5)
ttk.Button(btns, text="Copy MGRS", command=copy_mgrs).grid(row=0, column=1, padx=5)

ttk.Separator(tab_single).grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=4)

ttk.Label(tab_single, text="MGRS").grid(row=5, column=0, sticky="w", **pad)
mgrs_var = tk.StringVar()
ttk.Entry(tab_single, textvariable=mgrs_var, width=38, state="readonly").grid(
    row=5, column=1, **pad
)

ttk.Label(tab_single, text="Lat (WGS84)").grid(row=6, column=0, sticky="w", **pad)
lat_var = tk.StringVar()
ttk.Entry(tab_single, textvariable=lat_var, width=38, state="readonly").grid(
    row=6, column=1, **pad
)

ttk.Label(tab_single, text="Lon (WGS84)").grid(row=7, column=0, sticky="w", **pad)
lon_var = tk.StringVar()
ttk.Entry(tab_single, textvariable=lon_var, width=38, state="readonly").grid(
    row=7, column=1, **pad
)

root.bind("<Return>", lambda _e: do_convert())

# ── Batch tab ──────────────────────────────────────────────────────────────────
tab_batch = ttk.Frame(nb)
nb.add(tab_batch, text="Paste & Convert")

ttk.Label(tab_batch, text="Paste X Y pairs (one per line, space or tab separated):").grid(
    row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 2)
)

batch_text = tk.Text(tab_batch, width=50, height=8, font=("Courier", 10))
batch_text.grid(row=1, column=0, columnspan=2, padx=10, pady=4)

ttk.Button(tab_batch, text="Convert All", command=do_batch).grid(
    row=2, column=0, columnspan=2, pady=6
)

ttk.Label(tab_batch, text="Results (X  Y  MGRS  Lat  Lon):").grid(
    row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(6, 2)
)

batch_result = tk.Text(tab_batch, width=80, height=10, font=("Courier", 10), state="disabled")
batch_result.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 10))

root.mainloop()
