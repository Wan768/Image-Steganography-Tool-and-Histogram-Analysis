import os
import struct
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image

def embed_file(cover_path: str, secret_path: str, output_path: str):
    with open(secret_path, "rb") as f:
        secret_bytes = f.read()

    ext_bytes = os.path.splitext(secret_path)[1].lower().encode('utf-8')
    header = struct.pack(">I", len(ext_bytes)) + ext_bytes + struct.pack(">I", len(secret_bytes))
    payload = header + secret_bytes

    bit_string = ''.join(f"{byte:08b}" for byte in payload)
    img = Image.open(cover_path).convert("RGB")
    pixels = list(img.getdata())

    if len(bit_string) > len(pixels) * 3:
        raise ValueError("Secret file size exceeds cover image storage capacity.")

    new_pixels = []
    bit_idx = 0
    for r, g, b in pixels:
        channels = [r, g, b]
        for i in range(3):
            if bit_idx < len(bit_string):
                channels[i] = (channels[i] & ~1) | int(bit_string[bit_idx])
                bit_idx += 1
        new_pixels.append(tuple(channels))

    stego_img = Image.new("RGB", img.size)
    stego_img.putdata(new_pixels)
    stego_img.save(output_path, "PNG")

def extract_file(stego_path: str, output_dir: str):
    img = Image.open(stego_path).convert("RGB")
    pixels = list(img.getdata())

    extracted_bits = [str(channel & 1) for pixel in pixels for channel in pixel]
    bit_str = "".join(extracted_bits)
    raw_bytes = bytearray(int(bit_str[i:i+8], 2) for i in range(0, len(bit_str), 8))

    ext_len = struct.unpack(">I", raw_bytes[:4])[0]
    ext = raw_bytes[4:4+ext_len].decode('utf-8')
    data_len = struct.unpack(">I", raw_bytes[4+ext_len:8+ext_len])[0]

    start_offset = 8 + ext_len
    secret_data = raw_bytes[start_offset : start_offset + data_len]

    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"extracted_file{ext}")
    with open(out_file, "wb") as f:
        f.write(secret_data)
    return out_file

class StegoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LSB Steganography Tool")
        self.geometry("520x300")
        self.resizable(False, False)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_encode = ttk.Frame(notebook)
        self.tab_decode = ttk.Frame(notebook)

        notebook.add(self.tab_encode, text="Encode (Hide File)")
        notebook.add(self.tab_decode, text="Decode (Extract File)")

        self._build_encode_tab()
        self._build_decode_tab()

    def _build_encode_tab(self):
        self.cover_path = tk.StringVar()
        self.secret_path = tk.StringVar()

        ttk.Label(self.tab_encode, text="Cover Image:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        ttk.Entry(self.tab_encode, textvariable=self.cover_path, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(self.tab_encode, text="Browse", command=lambda: self._browse_file(self.cover_path, "Images", "*.png;*.jpg;*.jpeg")).grid(row=0, column=2, padx=5)

        ttk.Label(self.tab_encode, text="Secret File:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        ttk.Entry(self.tab_encode, textvariable=self.secret_path, width=40).grid(row=1, column=1, padx=5)
        ttk.Button(self.tab_encode, text="Browse", command=lambda: self._browse_file(self.secret_path, "All Files", "*.*")).grid(row=1, column=2, padx=5)

        ttk.Button(self.tab_encode, text="Encode & Save Stego Image", command=self._run_encode).grid(row=2, column=0, columnspan=3, pady=25)

    def _build_decode_tab(self):
        self.stego_path = tk.StringVar()

        ttk.Label(self.tab_decode, text="Stego Image:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        ttk.Entry(self.tab_decode, textvariable=self.stego_path, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(self.tab_decode, text="Browse", command=lambda: self._browse_file(self.stego_path, "PNG Images", "*.png")).grid(row=0, column=2, padx=5)

        ttk.Button(self.tab_decode, text="Extract Hidden File", command=self._run_decode).grid(row=1, column=0, columnspan=3, pady=25)

    def _browse_file(self, target_var, file_type_label, file_pattern):
        file_selected = filedialog.askopenfilename(filetypes=[(file_type_label, file_pattern)])
        if file_selected:
            target_var.set(file_selected)

    def _run_encode(self):
        if not self.cover_path.get() or not self.secret_path.get():
            messagebox.showwarning("Missing Input", "Please select both a cover image and a secret file.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if save_path:
            try:
                embed_file(self.cover_path.get(), self.secret_path.get(), save_path)
                messagebox.showinfo("Success", f"Stego image created successfully:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _run_decode(self):
        if not self.stego_path.get():
            messagebox.showwarning("Missing Input", "Please select a stego image to decode.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder")
        if output_dir:
            try:
                out_file = extract_file(self.stego_path.get(), output_dir)
                messagebox.showinfo("Success", f"File extracted successfully:\n{out_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract payload: {str(e)}")

if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()