
## 3. Cài Đặt SignTool.exe (Bắt buộc để ký số)

`SignTool` là công cụ của Microsoft dùng để gắn chữ ký số vào file `.exe`. Nếu script build báo lỗi "SignTool.exe not found", bạn cần làm như sau:

**Cách 1: Cài đặt Windows SDK (Chính thống)**
1.  Tải **Windows SDK** từ Microsoft: [Link tải](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/)
2.  Chạy bộ cài, chọn **"Windows SDK Signing Tools for Desktop Apps"** (các thành phần khác có thể bỏ chọn để nhẹ máy).
3.  Sau khi cài, đường dẫn thường là:
    - `C:\Program Files (x86)\Windows Kits\10\bin\10.0.xxxxx.0\x64\signtool.exe`
4.  Cập nhật đường dẫn này vào file `build_installer.py` (biến `SIGN_TOOL_PATH`).

**Cách 2: Tải riêng SignTool (Nhanh)**
1.  Tìm tải file `signtool.exe` (phiên bản 64-bit) từ các nguồn chia sẻ uy tín hoặc copy từ máy đã cài Visual Studio.
2.  Đặt file `signtool.exe` ngay tại thư mục chứa mã nguồn dự án (`D:\FolderSizeManager\FolderSizeManagerPy`).
3.  Script build sẽ tự động tìm thấy nó tại đây.
