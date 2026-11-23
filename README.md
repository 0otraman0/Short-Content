# YouTube Shorts Generator - Mind-Blowing Facts & Minecraft Parkour

Công cụ tạo video ngắn YouTube Shorts dọc (9:16) hoàn toàn **cục bộ (local)** trên Windows, tự động ghép giọng đọc kịch bản khoa học / sự thật lôi cuốn lên nền gameplay Minecraft parkour cùng phụ đề chữ nổi bật (burned-in captions).

---

## 1. Yêu cầu hệ thống & Cài đặt tiên quyết (Prerequisites)

1. **Hệ điều hành**: Windows 10 hoặc 11 (64-bit), tối thiểu 16 GB RAM. Hỗ trợ tăng tốc phần cứng bằng card NVIDIA (h264_nvenc) và tự động dùng CPU nếu không có GPU rời.
2. **Python**: Phiên bản **3.11** trở lên.
   - Tải tại: [python.org/downloads](https://www.python.org/downloads/)
   - *Lưu ý quan trọng*: Khi cài đặt nhớ tích chọn **"Add python.exe to PATH"**.
3. **FFmpeg** (Bắt buộc để xử lý video và âm thanh):
   - Mở PowerShell hoặc Terminal trên Windows và chạy lệnh cài đặt nhanh qua Winget:
     ```powershell
     winget install Gyan.FFmpeg
     ```
   - Sau khi cài xong, kiểm tra bằng lệnh:
     ```powershell
     ffmpeg -version
     ```
4. **Google Gemini API Key** (Hoàn toàn miễn phí):
   - Truy cập [Google AI Studio](https://aistudio.google.com/) và tạo một API key miễn phí.

---

## 2. Cấu hình ban đầu

1. **Tạo file môi trường `.env`**:
   - Sao chép file `.env.example` thành `.env` (hoặc chạy `start.bat` để được tạo tự động).
   - Mở `.env` và điền key của bạn:
     ```env
     GEMINI_API_KEY=AIzaSy...your_actual_key_here
     ```
2. **Cấu hình tùy chọn trong `config.yaml`**:
   - `gemini.model`: Model Gemini miễn phí đang sử dụng (mặc định: `gemini-2.5-flash`).
   - `tts.voice`: Giọng đọc nam tiếng Anh cố định (mặc định: `en-US-ChristopherNeural`).
   - `pacing_presets`: Tùy chỉnh các preset nhịp điệu (Mystery, Hype, Calm).

---

## 3. Thư mục nguyên liệu (Assets)

- **`assets/minecraft/`**: Thả các video clip Minecraft parkour định dạng `.mp4` vào đây. Nếu chưa có video, hệ thống sẽ tự động dùng hình nền đen placeholder.
- **`assets/music/`**: Thả các bài nhạc nền không lời định dạng `.mp3`. Hệ thống sẽ tự động giảm âm lượng nhạc (-22 dB) phía dưới giọng đọc.

---

## 4. Khởi chạy ứng dụng

Chỉ cần **nhấp đúp chuột vào file `start.bat`** (hoặc chạy từ cửa sổ dòng lệnh):
```cmd
start.bat
```
File này sẽ tự động:
1. Tạo môi trường ảo `venv` nếu chưa có.
2. Kích hoạt môi trường và cài đặt các thư viện cần thiết.
3. Kiểm tra FFmpeg và tạo file `.env` mẫu.
4. Bật máy chủ FastAPI và tự động mở trình duyệt tại `http://127.0.0.1:8000`.

---

## 5. Hướng dẫn sử dụng tính năng nhịp điệu (Pacing Markup)

Trong kịch bản tiếng Anh, bạn có thể chèn các thẻ sau để giọng đọc cuốn hút và tự nhiên hơn:
- `[pause 0.5]`: Nghỉ ngơi trong 0.5 giây (hoặc số giây tùy chọn).
- `[slow]...[/slow]`: Giọng đọc chậm lại (~ -15%) để tạo sự trầm lắng, hồi hộp.
- `[fast]...[/fast]`: Đọc dồn dập, nhanh hơn (~ +12%) cho phần mở đầu lôi cuốn.
- `*từ hoặc cụm từ*`: Nhấn giọng mạnh hơn, âm lượng cao hơn một chút.
- `[whisper]...[/whisper]`: Giọng thì thầm, nhỏ nhẹ và bí ẩn.

---

## 6. Xử lý sự cố thường gặp (Troubleshooting)

- **Lỗi: 'python' is not recognized as an internal or external command**:
  - Gỡ và cài lại Python, chú ý tích chọn ô **"Add python.exe to PATH"**.
- **Lỗi: FFmpeg không tìm thấy**:
  - Hãy chắc chắn đã chạy `winget install Gyan.FFmpeg` và khởi động lại cửa sổ Command Prompt/PowerShell để PATH được cập nhật.
- **Lỗi: Gemini API Rate Limit hoặc Invalid Key**:
  - Kiểm tra lại xem đã dán chính xác API key vào `.env` chưa, không để thừa dấu cách hay dấu ngoặc kép.
