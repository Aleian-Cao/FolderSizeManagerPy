import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from send2trash import send2trash

# --- CONFIG ---
WINRAR_PATH = r"C:\Program Files\WinRAR\WinRAR.exe"
if not os.path.exists(WINRAR_PATH):
    WINRAR_PATH = r"C:\Program Files (x86)\WinRAR\WinRAR.exe"

class FolderSizeManagerApp:
    def __init__(self, root, initial_path=None):
        self.root = root
        self.root.title("Folder Size Manager (Python Vibe)")
        self.root.geometry("1000x700")
        
        # Set icon if exists
        try:
            self.root.iconbitmap("app.ico")
        except:
            pass

        # Styles
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        
        # --- TOP PANEL ---
        frame_top = tk.Frame(root, pady=10)
        frame_top.pack(fill=tk.X, padx=10)

        tk.Label(frame_top, text="Thư mục:").pack(side=tk.LEFT)
        
        self.path_var = tk.StringVar()
        if initial_path and os.path.exists(initial_path):
            self.path_var.set(initial_path)
        else:
            self.path_var.set("C:\\")
            
        self.entry_path = tk.Entry(frame_top, textvariable=self.path_var, width=80)
        self.entry_path.pack(side=tk.LEFT, padx=5)

        tk.Button(frame_top, text="Chọn...", command=self.browse_folder).pack(side=tk.LEFT)
        
        self.btn_scan = tk.Button(frame_top, text="QUÉT (SCAN)", bg="lightblue", width=15, command=self.start_scan)
        self.btn_scan.pack(side=tk.LEFT, padx=10)

        # --- PROGRESS BAR ---
        self.progress = ttk.Progressbar(frame_top, mode='indeterminate', length=200)
        # self.progress.pack(side=tk.LEFT, padx=10) # Hidden by default

        # --- TREEVIEW ---
        columns = ("name", "type", "size", "path")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("name", text="Tên (Name)")
        self.tree.heading("type", text="Loại (Type)")
        self.tree.heading("size", text="Dung lượng")
        self.tree.heading("path", text="Đường dẫn")
        
        self.tree.column("name", width=300)
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("size", width=120, anchor="e")
        self.tree.column("path", width=400)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- STATUS BAR ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready.")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- CONTEXT MENU ---
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Mở thư mục", command=self.open_folder)
        self.menu.add_command(label="Copy đường dẫn", command=self.copy_path)
        self.menu.add_separator()
        self.menu.add_command(label="Chuyển vào Thùng Rác", command=self.move_to_recycle_bin, foreground="red")
        self.menu.add_command(label="Nén WinRAR và Xoá gốc", command=self.winrar_zip_delete, foreground="blue")
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Auto scan if initial path provided
        if initial_path and os.path.exists(initial_path):
            self.root.after(500, self.start_scan)

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

        # Disable button
        self.btn_scan.config(state=tk.DISABLED)
        self.status_var.set("Đang quét... Vui lòng chờ.")
        
        # Show progress
        self.progress.pack(side=tk.LEFT, padx=10)
        self.progress.start(10)
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Run in thread
        threading.Thread(target=self.scan_thread, args=(path,), daemon=True).start()

    def scan_thread(self, path):
        data = []
        try:
            # Scan folders
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        if entry.is_dir():
                            size = self.get_folder_size(entry.path)
                            data.append((entry.name, "Folder", size, entry.path))
                        elif entry.is_file():
                            size = entry.stat().st_size
                            data.append((entry.name, "File", size, entry.path))
                    except PermissionError:
                        continue
        except Exception as e:
            pass

        # Sort by size desc
        data.sort(key=lambda x: x[2], reverse=True)

        # Update UI
        self.root.after(0, self.update_ui, data)

    def update_ui(self, data):
        for item in data:
            name, type_, size, path = item
            self.tree.insert("", tk.END, values=(name, type_, self.format_size(size), path))
        
        self.btn_scan.config(state=tk.NORMAL)
        self.status_var.set(f"Hoàn thành. Tìm thấy {len(data)} mục.")
        
        # Hide progress
        self.progress.stop()
        self.progress.pack_forget()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def get_selected(self):
        selected = self.tree.selection()
        if not selected:
            return None
        return self.tree.item(selected[0])['values']

    def open_folder(self):
        item = self.get_selected()
        if item:
            path = item[3]
            if os.path.exists(path):
                if os.path.isfile(path):
                    subprocess.Popen(f'explorer /select,"{path}"')
                else:
                    os.startfile(path)

    def copy_path(self):
        item = self.get_selected()
        if item:
            path = item[3]
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            self.status_var.set(f"Đã copy: {path}")

    def move_to_recycle_bin(self):
        item = self.get_selected()
        if item:
            name = item[0]
            path = item[3]
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn chuyển '{name}' vào Thùng Rác?"):
                try:
                    send2trash(path)
                    self.tree.delete(self.tree.selection()[0])
                    self.status_var.set(f"Đã chuyển vào thùng rác: {name}")
                except Exception as e:
                    messagebox.showerror("Lỗi", str(e))

    def winrar_zip_delete(self):
        item = self.get_selected()
        if item:
            name = item[0]
            path = item[3]
            
            if not os.path.exists(WINRAR_PATH):
                messagebox.showerror("Lỗi", f"Không tìm thấy WinRAR tại {WINRAR_PATH}")
                return

            if messagebox.askyesno("Xác nhận WinRAR", f"Nén '{name}' và XOÁ gốc?"):
                parent = os.path.dirname(path)
                archive_name = f"{name}.rar"
                archive_path = os.path.join(parent, archive_name)
                
                # WinRAR CLI: a -df -ep1 "archive" "source"
                cmd = [WINRAR_PATH, "a", "-df", "-ep1", archive_path, path]
                
                # Show progress
                self.progress.pack(side=tk.LEFT, padx=10)
                self.progress.start(10)
                self.btn_scan.config(state=tk.DISABLED)

                def run_winrar():
                    try:
                        subprocess.run(cmd, check=True)
                        self.root.after(0, lambda: self.tree.delete(self.tree.selection()[0]))
                        self.root.after(0, lambda: self.status_var.set(f"Đã nén và xoá: {name}"))
                        self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã nén và xoá file gốc!"))
                    except subprocess.CalledProcessError:
                        self.root.after(0, lambda: messagebox.showerror("Lỗi", "WinRAR gặp lỗi khi nén."))
                    finally:
                        self.root.after(0, lambda: self.progress.stop())
                        self.root.after(0, lambda: self.progress.pack_forget())
                        self.root.after(0, lambda: self.btn_scan.config(state=tk.NORMAL))

                threading.Thread(target=run_winrar, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Handle args
    initial_path = None
    if len(sys.argv) > 1:
        initial_path = sys.argv[1]
        
    app = FolderSizeManagerApp(root, initial_path)
    root.mainloop()
