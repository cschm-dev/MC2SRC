"""GUI for the Minecraft to Source VMF Converter (English, two-column layout)"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import traceback
import json
import os
from .vmf_builder import convert_to_vmf


class MinecraftToSourceUI:
    """Tkinter GUI for the Minecraft to VMF converter"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Minecraft to Source VMF Converter")
        self.window.geometry("900x600")
        # Path to config file
        self.config_file = "converter_settings.json"
        # Variables
        self.world_path = tk.StringVar(value="")
        self.output_path = tk.StringVar(value="minecraft_export.vmf")
        self.x1 = tk.StringVar(value="0")
        self.z1 = tk.StringVar(value="0")
        self.x2 = tk.StringVar(value="100")
        self.z2 = tk.StringVar(value="100")
        self.y_min = tk.StringVar(value="-64")
        self.y_max = tk.StringVar(value="320")
        self.materials_path = tk.StringVar(value="minecraft")
        self.face_mapping = tk.StringVar(value="standard")
        self.force_ns = tk.BooleanVar(value=False)
        self.force_ew = tk.BooleanVar(value=False)
        self.group_mode = tk.StringVar(value="group_blocks")
        self.merge_blocks = tk.BooleanVar(value=True)
        self.texture_scale_x = tk.DoubleVar(value=1.0)
        self.texture_scale_y = tk.DoubleVar(value=1.0)
        # Load saved settings
        self.load_settings()
        self.setup_ui()

    def load_settings(self):
        """Load saved settings from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.world_path.set(settings.get("world_path", ""))
                self.output_path.set(settings.get("output_path", "minecraft_export.vmf"))
                self.x1.set(settings.get("x1", "0"))
                self.z1.set(settings.get("z1", "0"))
                self.x2.set(settings.get("x2", "100"))
                self.z2.set(settings.get("z2", "100"))
                self.y_min.set(settings.get("y_min", "-64"))
                self.y_max.set(settings.get("y_max", "320"))
                self.materials_path.set(settings.get("materials_path", "minecraft"))
                self.face_mapping.set(settings.get("face_mapping", "standard"))
                self.force_ns.set(settings.get("force_ns", False))
                self.force_ew.set(settings.get("force_ew", False))
                self.group_mode.set(settings.get("group_mode", "group_blocks"))
                self.merge_blocks.set(settings.get("merge_blocks", True))
                self.texture_scale_x.set(settings.get("texture_scale_x", 1.0))
                self.texture_scale_y.set(settings.get("texture_scale_y", 1.0))
                print(f"Settings loaded from {self.config_file}")
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save current settings to a JSON file"""
        settings = {
            "world_path": self.world_path.get(),
            "output_path": self.output_path.get(),
            "x1": self.x1.get(),
            "z1": self.z1.get(),
            "x2": self.x2.get(),
            "z2": self.z2.get(),
            "y_min": self.y_min.get(),
            "y_max": self.y_max.get(),
            "materials_path": self.materials_path.get(),
            "face_mapping": self.face_mapping.get(),
            "force_ns": self.force_ns.get(),
            "force_ew": self.force_ew.get(),
            "group_mode": self.group_mode.get(),
            "merge_blocks": self.merge_blocks.get(),
            "texture_scale_x": self.texture_scale_x.get(),
            "texture_scale_y": self.texture_scale_y.get()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            print(f"Settings saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def setup_ui(self):
        """Create the UI elements (two-column layout, all English)"""
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        left = tk.Frame(main_frame)
        left.pack(side="left", fill="both", expand=True, padx=(0,10))
        right = tk.Frame(main_frame)
        right.pack(side="right", fill="both", expand=True)

        # Paths
        path_frame = ttk.LabelFrame(left, text="Paths", padding="10")
        path_frame.pack(fill="x", pady=5)
        ttk.Label(path_frame, text="Minecraft World:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(path_frame, textvariable=self.world_path, width=30).grid(row=0, column=1, padx=5)
        ttk.Button(path_frame, text="Browse", command=self.browse_world).grid(row=0, column=2)
        ttk.Label(path_frame, text="VMF Output:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(path_frame, textvariable=self.output_path, width=30).grid(row=1, column=1, padx=5)
        ttk.Button(path_frame, text="Browse", command=self.browse_output).grid(row=1, column=2)

        # Coordinates
        coord_frame = ttk.LabelFrame(left, text="Coordinates", padding="10")
        coord_frame.pack(fill="x", pady=5)
        coords = [("X1:", self.x1), ("Z1:", self.z1), ("X2:", self.x2), ("Z2:", self.z2)]
        for i, (lbl, var) in enumerate(coords):
            ttk.Label(coord_frame, text=lbl).grid(row=i//2, column=(i%2)*2, padx=5, pady=2)
            ttk.Entry(coord_frame, textvariable=var, width=10).grid(row=i//2, column=(i%2)*2+1, padx=5, pady=2)

        # Height
        height_frame = ttk.LabelFrame(left, text="Height", padding="10")
        height_frame.pack(fill="x", pady=5)
        ttk.Label(height_frame, text="Y Min:").grid(row=0, column=0, padx=5)
        ttk.Entry(height_frame, textvariable=self.y_min, width=10).grid(row=0, column=1, padx=5)
        ttk.Label(height_frame, text="Y Max:").grid(row=0, column=2, padx=5)
        ttk.Entry(height_frame, textvariable=self.y_max, width=10).grid(row=0, column=3, padx=5)

        # Materials
        mat_frame = ttk.LabelFrame(left, text="Materials Path", padding="10")
        mat_frame.pack(fill="x", pady=5)
        ttk.Label(mat_frame, text="Path:").grid(row=0, column=0, padx=5)
        ttk.Entry(mat_frame, textvariable=self.materials_path, width=20).grid(row=0, column=1, padx=5)

        # Nodraw Optimization
        nodraw_frame = ttk.LabelFrame(left, text="Nodraw Optimization", padding="10")
        nodraw_frame.pack(fill="x", pady=5)
        ttk.Checkbutton(nodraw_frame, text="Disable nodraw for North/South", variable=self.force_ns).pack(anchor="w", pady=2)
        ttk.Checkbutton(nodraw_frame, text="Disable nodraw for East/West", variable=self.force_ew).pack(anchor="w", pady=2)

        # Face Mapping
        debug_frame = ttk.LabelFrame(right, text="Face Mapping", padding="10")
        debug_frame.pack(fill="x", pady=5)
        mappings = [
            ("standard", "Standard"),
            ("swap_ns", "Swap N/S"),
            ("swap_ew", "Swap E/W"),
            ("swap_both", "Swap Both")
        ]
        for val, txt in mappings:
            ttk.Radiobutton(debug_frame, text=txt, variable=self.face_mapping, value=val).pack(anchor="w", pady=2)

        # Grouping Option
        grouping_frame = ttk.LabelFrame(right, text="Grouping", padding="10")
        grouping_frame.pack(fill="x", pady=5)
        ttk.Radiobutton(grouping_frame, text="Group full blocks (1x1x1)", variable=self.group_mode, value="group_blocks").pack(anchor="w", pady=2)
        ttk.Radiobutton(grouping_frame, text="Group non-full blocks (fence, stairs, slabs, etc.)", variable=self.group_mode, value="group_nonfull_blocks").pack(anchor="w", pady=2)
        ttk.Radiobutton(grouping_frame, text="No Group", variable=self.group_mode, value="no_group").pack(anchor="w", pady=2)

        # Block Merging (Greedy Mesh)
        merge_frame = ttk.LabelFrame(right, text="Block Merging (Optimization)", padding="10")
        merge_frame.pack(fill="x", pady=5)
        ttk.Checkbutton(merge_frame, text="Enable greedy meshing (merge same blocks into larger rectangles)", variable=self.merge_blocks).pack(anchor="w", pady=2)
        ttk.Label(merge_frame, text="Reduces brush count drastically → fewer portal/T-junction errors, faster compilation", foreground="gray").pack(anchor="w", padx=20)

        # Texture Scale
        texture_frame = ttk.LabelFrame(right, text="Texture Scale", padding="10")
        texture_frame.pack(fill="x", pady=5)
        ttk.Label(texture_frame, text="Scale X:").grid(row=0, column=0, padx=5)
        ttk.Entry(texture_frame, textvariable=self.texture_scale_x, width=10).grid(row=0, column=1, padx=5)
        ttk.Label(texture_frame, text="Scale Y:").grid(row=0, column=2, padx=5)
        ttk.Entry(texture_frame, textvariable=self.texture_scale_y, width=10).grid(row=0, column=3, padx=5)
        ttk.Label(texture_frame, text="Direct UV scale values (1.0 = 64 units per texture repeat)", foreground="gray").grid(row=1, column=0, columnspan=4, pady=5)

        # Button Frame for Convert and Reset
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill="x", padx=20, pady=10)
        tk.Button(button_frame, text="CONVERT", command=self.convert, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), height=2).pack(fill="x", pady=5)
        tk.Button(button_frame, text="Reset Settings", command=self.reset_settings, bg="#FF9800", fg="white", font=("Arial", 10)).pack(fill="x", pady=5)

    def browse_world(self):
        """Select a world folder"""
        path = filedialog.askdirectory(title="Select Minecraft World")
        if path:
            self.world_path.set(path)

    def browse_output(self):
        """Select an output file"""
        path = filedialog.asksaveasfilename(defaultextension=".vmf", filetypes=[("VMF", "*.vmf")])
        if path:
            self.output_path.set(path)

    def reset_settings(self):
        """Reset all settings to default values"""
        if messagebox.askyesno("Confirmation", "Do you really want to reset all settings?"):
            # Set to default values
            self.world_path.set("")
            self.output_path.set("minecraft_export.vmf")
            self.x1.set("0")
            self.z1.set("0")
            self.x2.set("100")
            self.z2.set("100")
            self.y_min.set("-64")
            self.y_max.set("320")
            self.materials_path.set("minecraft")
            self.face_mapping.set("standard")
            self.force_ns.set(False)
            self.force_ew.set(False)
            self.group_mode.set("group_blocks")
            self.merge_blocks.set(True)
            self.texture_scale_x.set(1.0)
            self.texture_scale_y.set(1.0)
            # Delete the saved configuration file
            if os.path.exists(self.config_file):
                try:
                    os.remove(self.config_file)
                    print(f"Configuration file {self.config_file} deleted")
                except Exception as e:
                    print(f"Error deleting configuration file: {e}")
            messagebox.showinfo("Reset", "Settings have been reset to default values!")

    def convert(self):
        """Start the conversion"""
        try:
            # Save settings BEFORE conversion
            self.save_settings()
            # Perform conversion
            convert_to_vmf(
                self.world_path.get(),
                int(self.x1.get()),
                int(self.z1.get()),
                int(self.x2.get()),
                int(self.z2.get()),
                self.output_path.get(),
                int(self.y_min.get()),
                int(self.y_max.get()),
                self.materials_path.get(),
                face_mapping=self.face_mapping.get(),
                force_ns=self.force_ns.get(),
                force_ew=self.force_ew.get(),
                group_mode=self.group_mode.get(),
                merge_blocks=self.merge_blocks.get(),
                texture_scale_x=self.texture_scale_x.get(),
                texture_scale_y=self.texture_scale_y.get()
            )
            messagebox.showinfo("Success", "Conversion completed!")
        except Exception as e:
            messagebox.showerror("Error", f"{str(e)}\n\n{traceback.format_exc()}")

    def run(self):
        """Start the GUI"""
        self.window.mainloop()