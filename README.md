# 🟥 Pyxel Tile

**Pyxel Tile** is a specialized tile optimization suite for Game Boy and GB Studio developers. It intelligently reduces unique tile counts to fit within hardware constraints ($192$ or $128$ unique tiles) while preserving color integrity and visual heterogeneity.



---

### 🚀 Key Features

* **Hard-Solid Sky Sacrifice:** A dedicated mode that targets tiles in a user-defined "Sky Zone" and collapses them into monolithic solid colors. This creates a "snowball effect" that rapidly frees up tile slots for more complex areas.
* **Palette-Safe Merging:** Unlike standard image reducers, Pyxel Tile ensures that merged tiles are snapped back to the original $4$-color palette of the "Keep" tile, preventing the creation of "illegal" color combinations.
* **Granular Sky Height:** A precise slider ($0\%$ to $100\%$) allows you to define exactly where the sacrificial zone ends and the detailed world begins.
* **Binary Mode Toggle:** Easily switch between aggressive sky-reduction and standard detail-preservation.
* **GB Studio Ready:** Default settings are optimized for the standard $192$ unique tile limit.

---

### 🛠 Usage

1.  **Load:** Import a quantized $4$-color PNG image (8px grid aligned).
2.  **Configure:** * Set your **Target Unique Tiles**.
    * Toggle **Sky Sacrifice** if your background has a large open sky.
    * Adjust the **Sky Zone Height** slider to match your horizon.
3.  **Execute:** Run the reduction and save your optimized background.

---

### 🎨 Technical Philosophy

Pyxel Tile balances **Hardware Constraints** and **Visual Heterogeneity**. Instead of simply blurring or downsampling the whole image, it targets the "flat" parts of your background (the sky) for absolute simplification. This allows the tool to spend the saved VRAM "budget" on the textures, dithering, and gradients of your foreground objects.



---

### 📄 Project Links

* **Source Code:** [Pyxel_Tile.py (main branch)](https://github.com/contactpyxelmorph-afk/Pyxel-Tile/blob/main/Pyxel_Tile.py)

---
*Developed by contactpyxelmorph-afk*
