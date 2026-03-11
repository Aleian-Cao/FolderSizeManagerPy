import os
import sys
import subprocess
import threading
import json
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from send2trash import send2trash

# --- CONFIG & THEME ---
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

WINRAR_PATH = r"C:\Program Files\WinRAR\WinRAR.exe"
if not os.path.exists(WINRAR_PATH):
    WINRAR_PATH = r"C:\Program Files (x86)\WinRAR\WinRAR.exe"

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".folder_size_manager_config.json")

class FolderSizeManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("FileSMPy (Ultimate Edition)")
        self.geometry("1200x800")
        
        # Icon Setup
        icon_path = os.path.join(os.path.dirname(__file__), "FolderSizeManagerPy 2 logo.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except:
                pass
        elif os.path.exists("app.ico"):
             try:
                self.iconbitmap("app.ico")
             except:
                pass

        # Save config on exit
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (LEFT) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Folder Manager", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Config: Max Depth
        self.label_depth = ctk.CTkLabel(self.sidebar_frame, text="Max Depth:", anchor="w")
        self.label_depth.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.var_depth = tk.IntVar(value=3)
        self.spin_depth = ctk.CTkEntry(self.sidebar_frame, textvariable=self.var_depth) # Use Entry for simplicity or Slider? Let's use Entry for now or custom spinbox logic
        self.spin_depth.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Config: Min Size
        self.label_minsize = ctk.CTkLabel(self.sidebar_frame, text="Min Size (GB):", anchor="w")
        self.label_minsize.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.var_minsize = tk.DoubleVar(value=0.1)
        self.spin_minsize = ctk.CTkEntry(self.sidebar_frame, textvariable=self.var_minsize)
        self.spin_minsize.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Config: Limit
        self.label_limit = ctk.CTkLabel(self.sidebar_frame, text="Display Limit:", anchor="w")
        self.label_limit.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.var_limit = tk.IntVar(value=50)
        self.spin_limit = ctk.CTkEntry(self.sidebar_frame, textvariable=self.var_limit)
        self.spin_limit.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Theme Switch
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Theme:", anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0), sticky="w")
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=10, column=0, padx=20, pady=(0, 20), sticky="ew")

        # --- MAIN CONTENT (RIGHT) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent") # Transparent to show window bg
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Top Bar: Path Input & Scan
        self.top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.path_var = tk.StringVar(value="C:\\")
        self.entry_path = ctk.CTkEntry(self.top_frame, textvariable=self.path_var, placeholder_text="Enter path...")
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.btn_browse = ctk.CTkButton(self.top_frame, text="Browse", width=80, command=self.browse_folder)
        self.btn_browse.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_scan = ctk.CTkButton(self.top_frame, text="SCAN NOW", width=120, fg_color="#2CC985", hover_color="#229966", command=self.start_scan)
        self.btn_scan.pack(side=tk.LEFT)

        # Progress Bar (Hidden by default)
        self.progress = ctk.CTkProgressBar(self.main_frame, mode="indeterminate", height=10)
        self.progress.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.progress.grid_remove() # Hide initially

        # --- TREEVIEW (Styled TTK) ---
        # CustomTkinter doesn't have a Treeview, so we use ttk.Treeview with Custom Style
        self.tree_frame = ctk.CTkFrame(self.main_frame) # Frame to hold tree and scrollbar
        self.tree_frame.grid(row=1, column=0, sticky="nsew")
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        # Style Configuration
        style = ttk.Style()
        style.theme_use("clam")
        
        # Colors based on CTK Theme (Approximate dark mode colors)
        bg_color = self._apply_appearance_mode(self.sidebar_frame._fg_color)
        text_color = "white" # simplified
        
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=40,
                        font=("Segoe UI", 16))
        style.map('Treeview', background=[('selected', '#1f538d')])
        
        style.configure("Treeview.Heading",
                        background="#3a3a3a",
                        foreground="white",
                        font=("Segoe UI", 16, "bold"),
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[('active', '#4a4a4a')])

        columns = ("type", "size", "path")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="tree headings", selectmode="browse")
        
        self.tree.heading("#0", text=" Name", anchor="w")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.heading("path", text="Full Path")
        
        self.tree.column("#0", width=400, anchor="w")
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("size", width=120, anchor="e")
        self.tree.column("path", width=300)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Bindings
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # --- CONTEXT MENU ---
        self.menu = tk.Menu(self, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#1f538d", activeforeground="white")
        self.menu.add_command(label="Open Folder", command=self.open_folder)
        self.menu.add_command(label="Copy Path", command=self.copy_path)
        self.menu.add_separator()
        self.menu.add_command(label="Move to Recycle Bin", command=self.move_to_recycle_bin)
        self.menu.add_command(label="WinRAR Zip & Delete", command=self.winrar_zip_delete)

        # --- STATUS BAR ---
        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready.", anchor="w", text_color="gray")
        self.status_label.grid(row=3, column=0, sticky="ew", pady=(5, 0))

        # --- INITIALIZATION ---
        self.load_config()
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            self.path_var.set(sys.argv[1])
            self.after(500, self.start_scan)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        # Update Treeview colors? (Complex requires restart or deep restyling)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    if "path" in config and os.path.exists(config["path"]):
                        self.path_var.set(config["path"])
                    if "depth" in config:
                        self.var_depth.set(config["depth"])
                    if "min_size" in config:
                        self.var_minsize.set(config["min_size"])
                    if "limit" in config:
                        self.var_limit.set(config["limit"])
            except:
                pass

    def save_config(self):
        config = {
            "path": self.path_var.get(),
            "depth": self.var_depth.get(),
            "min_size": self.var_minsize.get(),
            "limit": self.var_limit.get()
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except:
            pass

    def on_close(self):
        self.stop_prefetch = True
        self.save_config()
        self.destroy()

    def browse_folder(self):
        folder = ctk.filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def get_folder_size(self, path):
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except:
            pass
        return total_size

    def start_scan(self):
        path = self.path_var.get()
        if not os.path.exists(path):
            messagebox.showerror("Error", "Path not found!")
            return

        self.btn_scan.configure(state="disabled")
        self.status_label.configure(text="Scanning...")
        self.progress.grid() # Show progress
        self.progress.start()
        
        # Clear tree & Cache
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.prefetch_cache = {}
        self.prefetch_queue = []
        self.stop_prefetch = False

        min_size_gb = self.var_minsize.get()
        threading.Thread(target=self.scan_level, args=(path, "", min_size_gb, True), daemon=True).start()

    def scan_level(self, path, parent_node, min_size_gb, is_root=False):
        items = []
        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        if entry.is_dir():
                            size = self.get_folder_size(entry.path)
                            if size >= (min_size_gb * 1024**3):
                                items.append((entry.name, "Folder", size, entry.path, True))
                        elif entry.is_file():
                            size = entry.stat().st_size
                            if size >= (min_size_gb * 1024**3):
                                items.append((entry.name, "File", size, entry.path, False))
                    except PermissionError:
                        continue
        except Exception:
            pass

        items.sort(key=lambda x: x[2], reverse=True)
        
        # If running in background (prefetch), return items
        if not is_root and threading.current_thread().name == "PrefetchWorker":
            return items

        self.after(0, self.update_tree, parent_node, items)
        
        # Add dirs to prefetch queue
        if is_root:
            for item in items:
                if item[4]: # is_dir
                    self.prefetch_queue.append(item[3])
            # Start prefetcher
            threading.Thread(target=self.prefetch_worker, args=(min_size_gb,), name="PrefetchWorker", daemon=True).start()

    def prefetch_worker(self, min_size_gb):
        while self.prefetch_queue and not self.stop_prefetch:
            path = self.prefetch_queue.pop(0)
            if path in self.prefetch_cache: continue
            
            # Scan
            items = self.scan_level(path, "", min_size_gb, False) # Returns items
            if items is not None:
                self.prefetch_cache[path] = items
                # Add next level to queue (Breadth First)
                # Only if depth < MaxDepth? For now unlimited prefetch or limited?
                # Let's limit prefetch to 2 levels deep from root to save RAM, or just keep going slowly
                # Let's just prefetch what's in queue.
                # NOTE: If we want deeper prefetch, we need to add children of children here.
                # For now, let's just prefetch Level 2 (children of root)
                pass

    def update_tree(self, parent_node, items):
        for item in items:
            name, type_, size, path, is_dir = item
            
            # Color Grading Logic
            size_gb = size / (1024**3)
            tags = ()
            if size_gb > 10:
                tags = ('huge',)
            elif size_gb > 1:
                tags = ('large',)
            elif size_gb > 0.1:
                tags = ('medium',)
            else:
                tags = ('small',)

            # Insert node
            node_id = self.tree.insert(parent_node, tk.END, text=f" {name}", values=(type_, self.format_size(size), path), open=False, tags=tags)
            
            if is_dir:
                self.tree.insert(node_id, tk.END, text="Loading...", values=("", "", ""))
        
        # Configure Tags colors
        self.tree.tag_configure('huge', foreground='#ff4d4d')   # Red
        self.tree.tag_configure('large', foreground='#ff944d')  # Orange
        self.tree.tag_configure('medium', foreground='#ffd633') # Yellow
        self.tree.tag_configure('small', foreground='#4dff88')  # Green

        if parent_node == "":
            self.btn_scan.configure(state="normal")
            self.status_label.configure(text="Scan Completed.")
            self.progress.stop()
            self.progress.grid_remove()

    def on_tree_open(self, event):
        item_id = self.tree.focus()
        if not item_id: return
            
        children = self.tree.get_children(item_id)
        if len(children) == 1 and self.tree.item(children[0], "text") == "Loading...":
            self.tree.delete(children[0])
            path = self.tree.item(item_id, "values")[2]
            min_size_gb = self.var_minsize.get()
            
            # Check cache
            if path in self.prefetch_cache:
                self.update_tree(item_id, self.prefetch_cache[path])
                return

            self.status_label.configure(text=f"Loading: {path}")
            self.progress.grid()
            self.progress.start()
            
            def load_sub():
                self.scan_level(path, item_id, min_size_gb)
                self.after(0, lambda: self.progress.stop())
                self.after(0, lambda: self.progress.grid_remove())
                
            threading.Thread(target=load_sub, daemon=True).start()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def get_selected(self):
        selected = self.tree.selection()
        if not selected: return None
        return self.tree.item(selected[0])

    def open_folder(self):
        item = self.get_selected()
        if item:
            path = item['values'][2]
            if os.path.exists(path):
                if os.path.isfile(path):
                    subprocess.Popen(f'explorer /select,"{path}"')
                else:
                    os.startfile(path)

    def copy_path(self):
        item = self.get_selected()
        if item:
            path = item['values'][2]
            self.clipboard_clear()
            self.clipboard_append(path)
            self.status_label.configure(text=f"Copied: {path}")

    def move_to_recycle_bin(self):
        item = self.get_selected()
        if item:
            name = item['text'].strip()
            path = item['values'][2]
            
            clean_path = path
            if clean_path.startswith("\\\\?\\"): clean_path = clean_path[4:]
                
            if messagebox.askyesno("Confirm", f"Move '{name}' to Recycle Bin?"):
                if not os.path.exists(clean_path):
                    messagebox.showerror("Error", "File not found!")
                    return
                try:
                    send2trash(clean_path)
                    self.tree.delete(self.tree.selection()[0])
                    self.status_label.configure(text=f"Deleted: {name}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def winrar_zip_delete(self):
        item = self.get_selected()
        if item:
            name = item['text'].strip()
            path = item['values'][2]
            
            if not os.path.exists(WINRAR_PATH):
                messagebox.showerror("Error", "WinRAR not found!")
                return

            if messagebox.askyesno("Confirm", f"Zip '{name}' and Delete original?"):
                parent = os.path.dirname(path)
                archive_path = os.path.join(parent, f"{name}.rar")
                cmd = [WINRAR_PATH, "a", "-df", "-ep1", archive_path, path]
                
                self.progress.grid()
                self.progress.start()
                self.btn_scan.configure(state="disabled")

                def run():
                    try:
                        subprocess.run(cmd, check=True)
                        self.after(0, lambda: self.tree.delete(self.tree.selection()[0]))
                        self.after(0, lambda: messagebox.showinfo("Success", "Archive created and original deleted."))
                    except:
                        self.after(0, lambda: messagebox.showerror("Error", "WinRAR failed."))
                    finally:
                        self.after(0, lambda: self.progress.stop())
                        self.after(0, lambda: self.progress.grid_remove())
                        self.after(0, lambda: self.btn_scan.configure(state="normal"))

                threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    app = FolderSizeManagerApp()
    app.mainloop()
