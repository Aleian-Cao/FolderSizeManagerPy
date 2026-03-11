# FileSMPy - Folder Size Manager

<div align="center">
  <img src="dist/FolderSizeManagerPy%202%20logo.png" alt="FileSMPy Logo" width="1173" height="128">
</div>

**FileSMPy** là ứng dụng quản lý dung lượng thư mục hiện đại, được viết bằng Python (CustomTkinter) với giao diện trực quan và hiệu năng cao.

## Tính năng nổi bật

- **Giao diện hiện đại (Modern UI):** Sử dụng CustomTkinter với chế độ Dark Mode, các widget bo tròn tinh tế.
- **Quét thông minh (Smart Scan):** Tự động quét ngầm các thư mục con để hiển thị tức thì khi mở rộng (Lazy Loading + Pre-fetching).
- **Trực quan hóa dữ liệu:**
  - Phân loại màu sắc theo dung lượng (Đỏ: Lớn, Xanh: Nhỏ).
  - Hiển thị Progress Bar khi đang xử lý tác vụ nặng.
- **Quản lý file mạnh mẽ:**
  - Xoá file/folder vào Thùng rác (Recycle Bin) an toàn.
  - Tích hợp WinRAR để nén thư mục.
  - Mở nhanh thư mục trong File Explorer.
- **Lưu cấu hình:** Tự động ghi nhớ đường dẫn quét cuối cùng và các thiết lập lọc.

## Cài đặt và Chạy từ mã nguồn

### Yêu cầu
- Python 3.9+
- Git

### Các bước thực hiện

1.  **Clone repository:**
    ```bash
    git clone <your-repo-url>
    cd FileSMPy
    ```

2.  **Tạo môi trường ảo (khuyên dùng):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    ```

3.  **Cài đặt thư viện:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Chạy ứng dụng:**
    ```bash
    python main_modern.py
    ```

## Đóng gói thành EXE

Để tạo file chạy độc lập (`.exe`), sử dụng lệnh sau:

```bash
pyinstaller --noconfirm --onefile --windowed --name "FileSMPy" --icon "FolderSizeManagerPy 2 logo.ico" --add-data ".venv\Lib\site-packages\customtkinter;customtkinter" --hidden-import "packaging" --hidden-import "customtkinter" --hidden-import "darkdetect" --hidden-import "PIL" --hidden-import "PIL.Image" "main_modern.py"
```

## Cấu trúc dự án

- `main_modern.py`: Mã nguồn chính của ứng dụng.
- `requirements.txt`: Danh sách các thư viện phụ thuộc.
- `FolderSizeManagerPy 2 logo.ico`: Icon ứng dụng.

## Tác giả

Phát triển bởi Aleian & Trae AI.
