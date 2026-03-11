import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from send2trash import send2trash

import json

# --- CONFIG ---
WINRAR_PATH = r"C:\Program Files\WinRAR\WinRAR.exe"
if not os.path.exists(WINRAR_PATH):
    WINRAR_PATH = r"C:\Program Files (x86)\WinRAR\WinRAR.exe"

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".folder_size_manager_config.json")

class FolderSizeManagerApp:
    def __init__(self, root, initial_path=None):
        self.root = root
        self.root.title("Folder Size Manager (Pro Edition)")
        self.root.geometry("1100x700")
        
        # Save config on exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        try:
            self.root.iconbitmap("app.ico")
        except:
            pass

        # --- LAYOUT MAIN ---
        # Sidebar (Left) - Config
        frame_left = tk.Frame(root, width=250, bg="#f0f0f0", padx=10, pady=10)
        frame_left.pack(side=tk.LEFT, fill=tk.Y)
        frame_left.pack_propagate(False)

        # Main Content (Right)
        frame_right = tk.Frame(root)
        frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- SIDEBAR CONTROLS ---
        tk.Label(frame_left, text="CẤU HÌNH QUÉT", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(0, 10))

        # Max Depth
        tk.Label(frame_left, text="Độ sâu (Max Depth):", bg="#f0f0f0").pack(anchor="w")
        self.var_depth = tk.IntVar(value=3)
        tk.Spinbox(frame_left, from_=1, to=10, textvariable=self.var_depth).pack(fill=tk.X, pady=(0, 10))

        # Min Size
        tk.Label(frame_left, text="Min Size (GB):", bg="#f0f0f0").pack(anchor="w")
        self.var_minsize = tk.DoubleVar(value=0.1)
        tk.Spinbox(frame_left, from_=0.0, to=100.0, increment=0.1, textvariable=self.var_minsize).pack(fill=tk.X, pady=(0, 10))

        # Top Count (Optional - logic filter display)
        tk.Label(frame_left, text="Giới hạn hiển thị:", bg="#f0f0f0").pack(anchor="w")
        self.var_limit = tk.IntVar(value=50)
        tk.Spinbox(frame_left, from_=10, to=500, textvariable=self.var_limit).pack(fill=tk.X, pady=(0, 10))

        tk.Label(frame_left, text="Ghi chú:", bg="#f0f0f0", fg="gray").pack(anchor="w", pady=(20, 0))
        tk.Label(frame_left, text="- Click mũi tên để mở rộng thư mục con.", bg="#f0f0f0", fg="gray", wraplength=230, justify=tk.LEFT).pack(anchor="w")
        tk.Label(frame_left, text="- Chuột phải để thao tác.", bg="#f0f0f0", fg="gray", wraplength=230, justify=tk.LEFT).pack(anchor="w")

        # --- TOP PANEL (RIGHT) ---
        frame_top = tk.Frame(frame_right, pady=10)
        frame_top.pack(fill=tk.X, padx=10)

        tk.Label(frame_top, text="Path:").pack(side=tk.LEFT)
        
        self.path_var = tk.StringVar()
        if initial_path and os.path.exists(initial_path):
            self.path_var.set(initial_path)
        else:
            self.path_var.set("C:\\")
            
        self.entry_path = tk.Entry(frame_top, textvariable=self.path_var)
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Button(frame_top, text="Browse...", command=self.browse_folder).pack(side=tk.LEFT)
        
        self.btn_scan = tk.Button(frame_top, text="QUÉT (SCAN)", bg="lightblue", width=15, command=self.start_scan)
        self.btn_scan.pack(side=tk.LEFT, padx=10)

        self.progress = ttk.Progressbar(frame_top, mode='indeterminate', length=150)

        # --- TREEVIEW (RIGHT) ---
        columns = ("type", "size", "path")
        self.tree = ttk.Treeview(frame_right, columns=columns, show="tree headings", selectmode="browse")
        
        # Define columns
        self.tree.heading("#0", text="Tên (Name)", anchor="w")
        self.tree.heading("type", text="Loại")
        self.tree.heading("size", text="Dung lượng")
        self.tree.heading("path", text="Đường dẫn đầy đủ")
        
        self.tree.column("#0", width=350, anchor="w")
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("size", width=100, anchor="e")
        self.tree.column("path", width=300)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Bind Expand Event
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- STATUS BAR ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")
        status_bar = tk.Label(frame_right, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- CONTEXT MENU ---
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Mở thư mục", command=self.open_folder)
        self.menu.add_command(label="Copy đường dẫn", command=self.copy_path)
        self.menu.add_separator()
        self.menu.add_command(label="Chuyển vào Thùng Rác", command=self.move_to_recycle_bin, foreground="red")
        self.menu.add_command(label="Nén WinRAR và Xoá gốc", command=self.winrar_zip_delete, foreground="blue")
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Auto scan
        if initial_path and os.path.exists(initial_path):
            self.root.after(500, self.start_scan)
        else:
            self.load_config()

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
        self.save_config()
        self.root.destroy()

    def browse_folder(self):
        folder = filedialog.askdirectory()
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
            messagebox.showerror("Lỗi", "Đường dẫn không tồn tại!")
            return

        self.btn_scan.config(state=tk.DISABLED)
        self.status_var.set("Đang quét... Vui lòng chờ.")
        self.progress.pack(side=tk.LEFT, padx=10)
        self.progress.start(10)
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Run Scan
        min_size_gb = self.var_minsize.get()
        threading.Thread(target=self.scan_level, args=(path, "", min_size_gb), daemon=True).start()

    def scan_level(self, path, parent_node, min_size_gb):
        # Scan immediate children only (Level 1)
        # Or scan deep to calculate size but only show level 1?
        # Better: Calculate size of all children, but only insert into Treeview the direct children.
        
        items = []
        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        if entry.is_dir():
                            size = self.get_folder_size(entry.path)
                            # Filter by min size
                            if size >= (min_size_gb * 1024**3):
                                items.append((entry.name, "Folder", size, entry.path, True))
                        elif entry.is_file():
                            size = entry.stat().st_size
                            # Show large files only if > min size? Or show all files if parent is shown?
                            # Let's show files > min_size too
                            if size >= (min_size_gb * 1024**3):
                                items.append((entry.name, "File", size, entry.path, False))
                    except PermissionError:
                        continue
        except Exception:
            pass

        # Sort desc
        items.sort(key=lambda x: x[2], reverse=True)

        self.root.after(0, self.update_tree, parent_node, items)

    def update_tree(self, parent_node, items):
        for item in items:
            name, type_, size, path, is_dir = item
            # Insert node
            node_id = self.tree.insert(parent_node, tk.END, text=name, values=(type_, self.format_size(size), path), open=False)
            
            # If directory, add a dummy child to make it expandable
            if is_dir:
                self.tree.insert(node_id, tk.END, text="Loading...", values=("", "", ""))
        
        if parent_node == "":
            self.btn_scan.config(state=tk.NORMAL)
            self.status_var.set("Hoàn thành.")
            self.progress.stop()
            self.progress.pack_forget()

    def on_tree_open(self, event):
        item_id = self.tree.focus()
        if not item_id:
            return
            
        # Check if already loaded (dummy child exists?)
        children = self.tree.get_children(item_id)
        if len(children) == 1 and self.tree.item(children[0], "text") == "Loading...":
            # Remove dummy
            self.tree.delete(children[0])
            
            # Get path
            path = self.tree.item(item_id, "values")[2]
            min_size_gb = self.var_minsize.get()
            
            # Load children in thread
            self.status_var.set(f"Đang tải: {path}")
            self.progress.pack(side=tk.LEFT, padx=10)
            self.progress.start(10)
            
            def load_sub():
                self.scan_level(path, item_id, min_size_gb)
                
            threading.Thread(target=load_sub, daemon=True).start()

    # --- ACTIONS (Copy from prev version) ---
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def get_selected(self):
        selected = self.tree.selection()
        if not selected: return None
        vals = self.tree.item(selected[0])['values']
        # vals is a list/tuple. [0]=type, [1]=size, [2]=path. (Name is in text)
        # Wait, Treeview values vs text logic:
        # text=Name, values=(Type, Size, Path)
        # So path is vals[2]
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
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            self.status_var.set(f"Đã copy: {path}")

    def move_to_recycle_bin(self):
        item = self.get_selected()
        if item:
            name = item['text']
            path = item['values'][2]
            
            # Normalize path (remove long path prefix if exists)
            clean_path = path
            if clean_path.startswith("\\\\?\\"):
                clean_path = clean_path[4:]
                
            if messagebox.askyesno("Xác nhận", f"Chuyển '{name}' vào Thùng Rác?"):
                if not os.path.exists(clean_path):
                    messagebox.showerror("Lỗi", "File/Thư mục không còn tồn tại!")
                    return

                try:
                    send2trash(clean_path)
                    self.tree.delete(self.tree.selection()[0])
                    self.status_var.set(f"Đã xoá: {name}")
                except Exception as e:
                    # Try fallback for long paths or permissions
                    messagebox.showerror("Lỗi", f"Không thể xoá: {str(e)}")

    def winrar_zip_delete(self):
        item = self.get_selected()
        if item:
            name = item['text']
            path = item['values'][2]
            
            if not os.path.exists(WINRAR_PATH):
                messagebox.showerror("Lỗi", f"Thiếu WinRAR tại {WINRAR_PATH}")
                return

            if messagebox.askyesno("Xác nhận", f"Nén '{name}' và XOÁ gốc?"):
                parent = os.path.dirname(path)
                archive_path = os.path.join(parent, f"{name}.rar")
                cmd = [WINRAR_PATH, "a", "-df", "-ep1", archive_path, path]
                
                self.progress.pack(side=tk.LEFT, padx=10)
                self.progress.start(10)
                
                def run():
                    try:
                        subprocess.run(cmd, check=True)
                        self.root.after(0, lambda: self.tree.delete(self.tree.selection()[0]))
                        self.root.after(0, lambda: messagebox.showinfo("Done", "Xong!"))
                    except:
                        self.root.after(0, lambda: messagebox.showerror("Error", "Lỗi WinRAR"))
                    finally:
                        self.root.after(0, lambda: self.progress.stop())
                        self.root.after(0, lambda: self.progress.pack_forget())

                threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    initial_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = FolderSizeManagerApp(root, initial_path)
    root.mainloop()
