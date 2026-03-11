# Lessons Learned - Folder Size Manager (Python Migration)

## Why Python?
- Phiên bản PowerShell Wrapper (Embedded Resource) gặp vấn đề tương thích trên một số máy (lỗi `CommandNotFound` hoặc bị chặn bởi Execution Policy).
- Python + Tkinter + PyInstaller tạo ra file `.exe` thực thụ (binary), ổn định hơn và ít phụ thuộc vào môi trường Shell.

## Architecture
- **GUI:** `tkinter` (Standard Library) - Đảm bảo chạy mượt mà, khởi động nhanh.
- **File Ops:** `send2trash` (Cross-platform Recycle Bin support) - An toàn hơn `os.remove`.
- **Packaging:** `PyInstaller --onefile --windowed` - Tạo 1 file exe duy nhất, không hiện cửa sổ console đen.

## Key Improvements
- **Multithreading:** Tác vụ Scan chạy trên thread riêng (`threading.Thread`), không làm đơ giao diện khi quét thư mục lớn.
- **Native Context Menu:** Menu chuột phải mượt mà hơn.
- **WinRAR Integration:** Gọi `subprocess` trực tiếp, kiểm soát lỗi tốt hơn.

## Known Issues
- Icon: Nếu build mà không tìm thấy file `.ico`, PyInstaller sẽ cảnh báo nhưng vẫn build thành công (dùng icon mặc định).
