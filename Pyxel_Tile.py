import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from collections import Counter
import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class GBStudioOptimizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pyxel Tile")
        self.root.geometry("500x700")
        self.root.configure(bg="#4a0000")

        try:
            self.root.iconbitmap(resource_path("log_ico.ico"))
        except:
            pass

        self.input_path = ""
        self.tile_limit = tk.IntVar(value=192)
        self.method = tk.StringVar(value="substitution")

        # FIX: Ensure sky_mode is an IntVar (0 or 1) for reliable checkbox behavior
        self.sky_mode = tk.IntVar(value=1)
        # FIX: Ensure sky_ratio is a DoubleVar for smooth slider percentages
        self.sky_ratio = tk.DoubleVar(value=0.35)

        self.create_widgets()

    def create_widgets(self):
        try:
            logo_img = Image.open(resource_path("log_png.png")).resize((140, 140), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            tk.Label(self.root, image=self.logo_photo, bg="#4a0000").pack(pady=15)
        except:
            tk.Label(self.root, text="PYXEL TILE", font=("Impact", 24), bg="#4a0000", fg="white").pack(pady=15)

        tk.Button(self.root, text="📁 LOAD PNG IMAGE", command=self.load_file, bg="#7d0000", fg="white",
                  font=("Arial", 10, "bold")).pack(pady=5)
        self.lbl_file = tk.Label(self.root, text="No file selected", bg="#4a0000", fg="#ffcccc", font=("Arial", 8))
        self.lbl_file.pack()

        frame = tk.LabelFrame(self.root, text=" ENGINE CONFIG ", bg="#4a0000", fg="white", padx=20, pady=20)
        frame.pack(pady=15, fill="x", padx=40)

        tk.Radiobutton(frame, text="Method: Substitution", variable=self.method, value="substitution", bg="#4a0000",
                       fg="white", selectcolor="#7d0000").pack(anchor="w")
        tk.Radiobutton(frame, text="Method: Merging", variable=self.method, value="merging", bg="#4a0000", fg="white",
                       selectcolor="#7d0000").pack(anchor="w")

        # Checkbox for Toggle (0 or 1)
        tk.Checkbutton(frame, text="🛑 ENABLE SKY SACRIFICE", variable=self.sky_mode, bg="#4a0000", fg="white",
                       selectcolor="#7d0000").pack(anchor="w", pady=10)

        # Slider for Range (0.1 to 1.0)
        tk.Label(frame, text="Sky Zone Height (Top %):", bg="#4a0000", fg="white").pack(anchor="w")
        tk.Scale(frame, from_=0.0, to=1.0, resolution=0.01, variable=self.sky_ratio, orient="horizontal", bg="#4a0000",
                 fg="white", highlightthickness=0).pack(fill="x")

        tk.Label(frame, text="Target Unique Tiles:", bg="#4a0000", fg="white").pack(side="left", pady=10)
        tk.Entry(frame, textvariable=self.tile_limit, width=6).pack(side="left", padx=10)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=350, mode="determinate")
        self.progress.pack(pady=20)

        tk.Button(self.root, text="START OPTIMIZATION", command=self.process, bg="#c0392b", fg="white",
                  font=("Arial", 11, "bold"), height=2, width=25).pack(pady=10)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("PNG images", "*.png")])
        if path:
            self.input_path = path
            self.lbl_file.config(text=os.path.basename(path))

    def get_dominant_color(self, tile):
        pixels = [tuple(p) for p in tile.reshape(-1, 3).astype(int)]
        return np.array(Counter(pixels).most_common(1)[0][0])

    def process(self):
        if not self.input_path: return
        img = Image.open(self.input_path).convert('RGB')
        data = np.array(img).astype(np.float32)
        h, w = data.shape[:2]

        tiles, is_sky_tile = [], []
        # Slider value determines the boundary
        sky_boundary = h * self.sky_ratio.get()

        for y in range(0, h, 8):
            for x in range(0, w, 8):
                tiles.append(data[y:y + 8, x:x + 8])
                # Only mark as sky if within the slider's range
                is_sky_tile.append(y < sky_boundary)

        tiles = np.array(tiles)
        unique_tiles, inverse = np.unique(tiles, axis=0, return_inverse=True)
        current_uniques = unique_tiles.copy()
        mapping = inverse.copy()

        unique_is_sky = np.zeros(len(current_uniques), dtype=bool)
        for i, u_idx in enumerate(inverse):
            if is_sky_tile[i]: unique_is_sky[u_idx] = True

        limit = self.tile_limit.get()
        num_to_reduce = len(current_uniques) - limit
        if num_to_reduce <= 0: return messagebox.showinfo("Info", "Under limit!")

        self.progress["maximum"] = num_to_reduce
        active_indices = list(range(len(current_uniques)))

        for step in range(num_to_reduce):
            num_active = len(active_indices)
            sky_pool = np.where(unique_is_sky[active_indices])[0]

            # Binary Toggle Check: Only use sky logic if sky_mode is 1
            if self.sky_mode.get() == 1 and len(sky_pool) > 0:
                flat_sky = current_uniques[active_indices][sky_pool].reshape(len(sky_pool), -1)
                local_remove_idx = sky_pool[np.argmax(np.std(flat_sky, axis=1))]
                g_idx = active_indices[local_remove_idx]
                current_uniques[g_idx][:, :] = self.get_dominant_color(current_uniques[g_idx])
            else:
                flat = current_uniques[active_indices].reshape(num_active, -1)
                local_remove_idx = np.argmin(np.std(flat, axis=1))

            target = current_uniques[active_indices[local_remove_idx]].reshape(-1)
            others_mask = np.arange(num_active) != local_remove_idx
            flat_all = current_uniques[active_indices].reshape(num_active, -1)
            distances = np.sum((flat_all[others_mask] - target) ** 2, axis=1)
            best_match_local = np.where(others_mask)[0][np.argmin(distances)]

            g_remove, g_keep = active_indices[local_remove_idx], active_indices[best_match_local]

            if self.method.get() == "merging" and not unique_is_sky[g_remove]:
                new_tile = (current_uniques[g_keep] + current_uniques[g_remove]) / 2
                palette = np.unique(current_uniques[g_keep].reshape(-1, 3), axis=0)
                for r in range(8):
                    for c in range(8):
                        d = np.sum((palette - new_tile[r, c]) ** 2, axis=1)
                        new_tile[r, c] = palette[np.argmin(d)]
                current_uniques[g_keep] = new_tile

            mapping[mapping == g_remove] = g_keep
            active_indices.pop(local_remove_idx)

            if step % 10 == 0:
                self.progress["value"] = step
                self.root.update()

        final = np.zeros_like(data)
        idx = 0
        for y in range(0, h, 8):
            for x in range(0, w, 8):
                final[y:y + 8, x:x + 8] = current_uniques[mapping[idx]]
                idx += 1

        save_p = filedialog.asksaveasfilename(defaultextension=".png")
        if save_p:
            Image.fromarray(np.clip(final, 0, 255).astype(np.uint8)).save(save_p)
            messagebox.showinfo("Done", "Optimized!")


if __name__ == "__main__":
    root = tk.Tk()
    app = GBStudioOptimizer(root)
    root.mainloop()