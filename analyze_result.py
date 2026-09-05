import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HistogramAnalysisApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Steganography Image & RGB Component Analyzer")
        self.geometry("850x680")
        self.resizable(True, True)

        self.cover_path = tk.StringVar()
        self.stego_path = tk.StringVar()

        self._build_gui()

    def _build_gui(self):
        # File Selection Area
        frame_inputs = ttk.LabelFrame(self, text=" Select Images ")
        frame_inputs.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame_inputs, text="Cover Image:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_inputs, textvariable=self.cover_path, width=55).grid(row=0, column=1, padx=5)
        ttk.Button(frame_inputs, text="Browse", command=lambda: self._browse_file(self.cover_path, "Images", "*.png;*.jpg;*.jpeg")).grid(row=0, column=2, padx=5)

        ttk.Label(frame_inputs, text="Stego Image:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(frame_inputs, textvariable=self.stego_path, width=55).grid(row=1, column=1, padx=5)
        ttk.Button(frame_inputs, text="Browse", command=lambda: self._browse_file(self.stego_path, "PNG Images", "*.png")).grid(row=1, column=2, padx=5)

        ttk.Button(frame_inputs, text="Analyze & Compare", command=self._run_analysis).grid(row=2, column=0, columnspan=3, pady=10)

        # Numerical Data Container Frame
        self.frame_stats = ttk.LabelFrame(self, text=" Numerical RGB Component Analysis ")
        self.frame_stats.pack(fill="x", padx=10, pady=5)

        self.lbl_stats = ttk.Label(self.frame_stats, text="Select both images and click 'Analyze & Compare'", font=("Consolas", 9), justify="left")
        self.lbl_stats.pack(anchor="w", padx=10, pady=5)

        # Plot Display Canvas Container
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.canvas = None

    def _browse_file(self, target_var, file_type_label, file_pattern):
        file_selected = filedialog.askopenfilename(filetypes=[(file_type_label, file_pattern)])
        if file_selected:
            target_var.set(file_selected)

    def _run_analysis(self):
        c_path = self.cover_path.get()
        s_path = self.stego_path.get()

        if not c_path or not s_path:
            messagebox.showwarning("Missing Input", "Please select both Cover and Stego images.")
            return

        try:
            # Load images as NumPy arrays for channel calculations
            cover_img = Image.open(c_path).convert("RGB")
            stego_img = Image.open(s_path).convert("RGB")

            c_arr = np.array(cover_img)
            s_arr = np.array(stego_img)

            # 1. File Size Metrics
            c_size = os.path.getsize(c_path) / 1024.0
            s_size = os.path.getsize(s_path) / 1024.0
            size_delta = s_size - c_size

            # 2. Exact RGB Component Metrics
            c_r_mean, c_g_mean, c_b_mean = c_arr[:, :, 0].mean(), c_arr[:, :, 1].mean(), c_arr[:, :, 2].mean()
            s_r_mean, s_g_mean, s_b_mean = s_arr[:, :, 0].mean(), s_arr[:, :, 1].mean(), s_arr[:, :, 2].mean()

            r_delta = s_r_mean - c_r_mean
            g_delta = s_g_mean - c_g_mean
            b_delta = s_b_mean - c_b_mean

            # Format statistics readout text
            stats_text = (
                f"FILE SIZES:  Cover: {c_size:.2f} KB | Stego: {s_size:.2f} KB | Diff: {size_delta:+.2f} KB\n"
                f"------------------------------------------------------------------------------------\n"
                f"COVER RGB MEANS:  Red: {c_r_mean:8.4f} | Green: {c_g_mean:8.4f} | Blue: {c_b_mean:8.4f}\n"
                f"STEGO RGB MEANS:  Red: {s_r_mean:8.4f} | Green: {s_g_mean:8.4f} | Blue: {s_b_mean:8.4f}\n"
                f"RGB MEAN DELTAS:  Red: {r_delta:+8.4f} | Green: {g_delta:+8.4f} | Blue: {b_delta:+8.4f}"
            )
            self.lbl_stats.config(text=stats_text)

            # 3. Plot RGB Histograms
            fig = Figure(figsize=(8, 3.5), dpi=100)
            ax_cover = fig.add_subplot(121)
            ax_stego = fig.add_subplot(122)

            colors = ('red', 'green', 'blue')
            for i, col in enumerate(colors):
                c_hist = cover_img.histogram()[i*256:(i+1)*256]
                s_hist = stego_img.histogram()[i*256:(i+1)*256]

                ax_cover.plot(c_hist, color=col, alpha=0.7)
                ax_stego.plot(s_hist, color=col, alpha=0.7)

            ax_cover.set_title(f"Cover RGB Histogram\n(R:{c_r_mean:.1f}, G:{c_g_mean:.1f}, B:{c_b_mean:.1f})", fontsize=9)
            ax_stego.set_title(f"Stego RGB Histogram\n(R:{s_r_mean:.1f}, G:{s_g_mean:.1f}, B:{s_b_mean:.1f})", fontsize=9)
            fig.tight_layout()

            # Refresh Canvas
            if self.canvas:
                self.canvas.get_tk_widget().destroy()

            self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze images: {str(e)}")

if __name__ == "__main__":
    app = HistogramAnalysisApp()
    app.mainloop()