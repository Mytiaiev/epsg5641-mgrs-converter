import tkinter as tk
from tkinter import ttk, messagebox

from pyproj import Transformer

# ── Coordinate transformers ────────────────────────────────────────────────────

# EPSG:5641 (SIRGAS 2000 / Brazil Mercator) -> WGS84
_to_wgs84 = Transformer.from_crs("EPSG:5641", "EPSG:4326", always_xy=True)

# ── Pure-Python MGRS conversion ───────────────────────────────────────────────

_LAT_BANDS = "CDEFGHJKLMNPQRSTUVWX"
_COL_LETTERS = ["ABCDEFGH", "JKLMNPQR", "STUVWXYZ"]
_ROW_LETTERS = "ABCDEFGHJKLMNPQRSTUV"


def _utm_zone(lon):
    return int((lon + 180) / 6) + 1


def _lat_band(lat):
    if lat < -80 or lat > 84:
        raise ValueError(f"Latitude {lat} outside MGRS range (-80..84)")
    idx = min(int((lat + 80) / 8), len(_LAT_BANDS) - 1)
    return _LAT_BANDS[idx]


def _100k_id(zone, easting, northing):
    set_col = (zone - 1) % 3
    set_row = (zone - 1) % 2
    e100k = int(easting // 100000)
    col = _COL_LETTERS[set_col][e100k - 1]
    n100k = int(northing % 2000000) // 100000
    row = _ROW_LETTERS[(n100k + set_row * 5) % 20]
    return col + row


def latlon_to_mgrs(lat, lon, precision=5):
    zone = _utm_zone(lon)
    # Norway / Svalbard exceptions
    if 56 <= lat < 64 and 3 <= lon < 12:
        zone = 32
    if 72 <= lat < 84:
        if 0 <= lon < 9:
            zone = 31
        elif 9 <= lon < 21:
            zone = 33
        elif 21 <= lon < 33:
            zone = 35
        elif 33 <= lon < 42:
            zone = 37

    is_north = lat >= 0
    utm = Transformer.from_crs(
        "EPSG:4326",
        f"+proj=utm +zone={zone} +{'north' if is_north else 'south'} +datum=WGS84",
        always_xy=True,
    )
    easting, northing = utm.transform(lon, lat)
    band = _lat_band(lat)
    sq = _100k_id(zone, easting, northing)

    e_rem = int(round(easting)) % 100000
    n_rem = int(round(northing)) % 100000
    d = 10 ** (5 - precision)
    return f"{zone:02d}{band}{sq}{e_rem // d:0{precision}d}{n_rem // d:0{precision}d}"


# ── Conversion wrapper ─────────────────────────────────────────────────────────

def convert_5641(x, y, precision=5):
    lon, lat = _to_wgs84.transform(x, y)
    mgrs_str = latlon_to_mgrs(lat, lon, precision)
    return mgrs_str, lat, lon


# ── GUI callbacks ──────────────────────────────────────────────────────────────

def do_convert():
    try:
        x = float(x_var.get().strip().replace(",", "."))
        y = float(y_var.get().strip().replace(",", "."))
    except ValueError:
        messagebox.showerror("Input error", "Enter valid numbers for X and Y.")
        return
    try:
        mgrs_string, lat, lon = convert_5641(x, y, precision_var.get())
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
    results, errors = [], []
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
            m, lat, lon = convert_5641(x, y, precision)
            results.append(f"{x:.0f}\t{y:.0f}\t{m}\t{lat:.8f}\t{lon:.8f}")
        except Exception as e:
            errors.append(f"Line {i}: {e}")
    batch_result.config(state="normal")
    batch_result.delete("1.0", tk.END)
    if results:
        batch_result.insert(tk.END, "X\tY\tMGRS\tLat\tLon\n" + "\n".join(results))
    if errors:
        batch_result.insert(tk.END, "\n\nErrors:\n" + "\n".join(errors))
    batch_result.config(state="disabled")


# ── UI ─────────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("EPSG:5641 → MGRS Converter")
root.resizable(False, False)

nb = ttk.Notebook(root)
nb.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

# ── Single tab ─────────────────────────────────────────────────────────────────
tab_single = ttk.Frame(nb)
nb.add(tab_single, text="Single")
pad = {"padx": 10, "pady": 6}

ttk.Label(tab_single, text="X (EPSG:5641)").grid(row=0, column=0, sticky="w", **pad)
x_var = tk.StringVar(value="13950085")
ttk.Entry(tab_single, textvariable=x_var, width=30).grid(row=0, column=1, **pad)

ttk.Label(tab_single, text="Y (EPSG:5641)").grid(row=1, column=0, sticky="w", **pad)
y_var = tk.StringVar(value="16156045")
ttk.Entry(tab_single, textvariable=y_var, width=30).grid(row=1, column=1, **pad)

ttk.Label(tab_single, text="Precision (1-5)").grid(row=2, column=0, sticky="w", **pad)
precision_var = tk.IntVar(value=5)
ttk.Spinbox(tab_single, from_=1, to=5, textvariable=precision_var, width=5).grid(
    row=2, column=1, sticky="w", **pad
)

btns = ttk.Frame(tab_single)
bns.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=8)
ttk.Button(btns, text="Convert", command=do_convert).grid(row=0, column=0, padx=5)
ttk.Button(btns, text="Copy MGRS", command=copy_mgrs).grid(row=0, column=1, padx=5)

ttk.Separator(tab_single).grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=4)

ttk.Label(tab_single, text="MGRS").grid(row=5, column=0, sticky="w", **pad)
mgrs_var = tk.StringVar()
ttk.Entry(tab_single, textvariable=mgrs_var, width=38, state="readonly").grid(row=5, column=1, **pad)

ttk.Label(tab_single, text="Lat (WGS84)").grid(row=6, column=0, sticky="w", **pad)
lat_var = tk.StringVar()
ttk.Entry(tab_single, textvariable=lat_var, width=38, state="readonly").grid(row=6, column=1, **pad)

ttk.Label(tab_single, text="Lon (WGS84)").grid(row=7, column=0, sticky="w", **pad)
lon_var = tk.StringVar()
ttk.Entry(tab_single, textvariable=lon_var, width=38, state="readonly").grid(row=7, column=1, **pad)

root.bind("<Return>", lambda _e: do_convert())

# ── Batch tab ──────────────────────────────────────────────────────────────────
tab_batch = ttk.Frame(nb)
bnb.add(tab_batch, text="Paste & Convert")

ttk.Label(tab_batch, text="Paste X Y pairs (one per line, space/tab separated):").grid(
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