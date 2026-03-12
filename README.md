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

## Đóng gói ứng dụng (Packaging)

Dự án hỗ trợ 2 phương thức đóng gói:
1.  **Portable (Chạy ngay):** File `.exe` độc lập, không cần cài đặt.
2.  **Installer (Chuyên nghiệp):** File cài đặt `.exe` với Setup Wizard, Shortcut Desktop, Context Menu, v.v.

### Cách thực hiện

1.  **Cài đặt Inno Setup:**
    - Tải và cài đặt [Inno Setup 6](https://jrsoftware.org/isdl.php).
    - Đảm bảo cài đặt đầy đủ các thành phần mặc định.

2.  **Chạy script đóng gói tự động:**
    Script này sẽ tự động build file Portable bằng PyInstaller và sau đó tạo bộ cài đặt bằng Inno Setup.

    ```bash
    python build_installer.py
    ```

    - **Output Portable:** `dist/FileSMPy.exe`
    - **Output Installer:** `dist/Install_FSMPy.exe`

### Cấu hình Installer (Nâng cao)
File cấu hình cho bộ cài đặt nằm tại `setup_script.iss`. Bạn có thể mở file này bằng Inno Setup Compiler để chỉnh sửa:
- Tên ứng dụng, phiên bản, nhà phát hành.
- Các tùy chọn Shortcut, Registry.
- Icon và hình ảnh.

## Hướng dẫn cài đặt cho người dùng (Self-signed)

Nếu bạn sử dụng chứng chỉ tự ký (Self-signed), người dùng cần cài đặt chứng chỉ này để Windows tin tưởng ứng dụng:

1.  Gửi file `MyCert.cer` cho người dùng.
2.  Hướng dẫn họ thực hiện:
    - Click đúp vào file `.cer`.
    - Chọn **Install Certificate**.
    - Chọn **Local Machine** -> Next.
    - Chọn **Place all certificates in the following store**.
    - Browse và chọn **Trusted Root Certification Authorities**.
    - Next -> Finish.
3.  Sau khi cài chứng chỉ, ứng dụng sẽ không còn bị cảnh báo "Unknown Publisher".

## Cấu trúc dự án

- `main_modern.py`: Mã nguồn chính của ứng dụng.
- `requirements.txt`: Danh sách các thư viện phụ thuộc.
- `FolderSizeManagerPy 2 logo.ico`: Icon ứng dụng.

## Tác giả

Phát triển bởi Aleian & Trae AI.
