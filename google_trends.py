import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
import os
import threading

# Define region codes for Google Trends
REGIONS = {
    "Greece (GR)": "GR",
    "Serbia (SR)": "SR",
    "Croatia (HR)": "HR",
    "Bulgaria (BG)": "BG",
    "Macedonia (MK)": "MK",
    "Romania (RO)": "RO",
    "Czechia (CZ)": "CZ",
    "Bosnia (BA)": "BA",
    "Slovakia (SK)": "SK",
    "Slovenia (SI)": "SI"
}


def fetch_google_trends(selected_codes, output_path, status_label):
    pytrends = TrendReq(hl='en-US', tz=360)
    all_data = []

    for code in selected_codes:
        try:
            df = pytrends.trending_searches(pn=code)
            df.columns = [f"Trending in {code}"]
            all_data.append(df)
        except Exception as e:
            print(f"Error fetching trends for {code}: {e}")
            continue

    if not all_data:
        messagebox.showerror("No Data", "No trend data could be retrieved.")
        return

    combined_df = pd.concat(all_data, axis=1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"google_trends_{timestamp}.csv"
    filepath = os.path.join(output_path, filename)
    combined_df.to_csv(filepath, index=False)

    status_label.config(text=f"✅ Trends saved to:\n{filepath}")
    messagebox.showinfo("Success", f"Trends data exported to:\n{filepath}")


def run_gui():
    root = tk.Tk()
    root.title("🌐 Google Trends Exporter")
    root.geometry("500x500")
    root.resizable(False, False)

    selected_vars = {}
    export_path = tk.StringVar()

    # --- Layout ---

    tk.Label(root, text="Select Regions to Track:", font=("Arial", 12, "bold")).pack(pady=(15, 5))

    region_frame = tk.Frame(root)
    region_frame.pack()

    for i, (name, code) in enumerate(REGIONS.items()):
        var = tk.BooleanVar(value=(code == "GR"))  # default select Greece
        cb = tk.Checkbutton(region_frame, text=name, variable=var)
        cb.grid(row=i // 2, column=i % 2, sticky="w", padx=10, pady=2)
        selected_vars[code] = var

    # Output folder selector
    tk.Label(root, text="Export Folder:", font=("Arial", 12)).pack(pady=(20, 5))
    path_frame = tk.Frame(root)
    path_frame.pack()

    path_entry = tk.Entry(path_frame, textvariable=export_path, width=40)
    path_entry.pack(side="left", padx=(10, 5))

    def browse_folder():
        path = filedialog.askdirectory()
        if path:
            export_path.set(path)

    browse_btn = tk.Button(path_frame, text="Browse", command=browse_folder)
    browse_btn.pack(side="left")

    # Status label
    status_label = tk.Label(root, text="Waiting for user action...", fg="gray")
    status_label.pack(pady=10)

    # Fetch trends
    def run_fetch_thread():
        status_label.config(text="Fetching Google Trends...")
        root.update_idletasks()
        selected = [code for code, var in selected_vars.items() if var.get()]

        if not selected:
            messagebox.showwarning("No Region", "Please select at least one region.")
            return
        if not export_path.get():
            messagebox.showwarning("No Folder", "Please select an export folder.")
            return

        threading.Thread(target=fetch_google_trends, args=(selected, export_path.get(), status_label)).start()

    tk.Button(root, text=" Fetch & Export Trends", command=run_fetch_thread,
              bg="#0078D7", fg="white", font=("Arial", 12)).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
    