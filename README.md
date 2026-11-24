# YouTube Shorts Narration Tool

**Công cụ tạo giọng đọc, phụ đề chuẩn SRT và nguồn dẫn chứng sự thật cho video ngắn YouTube Shorts.**
Ứng dụng chạy hoàn toàn **cục bộ (local)** trên hệ điều hành Windows qua giao diện web hiện đại, không phát sinh chi phí và không phụ thuộc vào dịch vụ trả phí nào.

---

## 1. Giới thiệu tổng quan (Overview)

Công cụ hỗ trợ nhà sáng tạo nội dung YouTube Shorts (chủ đề "sự thật khoa học / fact kỳ thú được kiểm chứng") từ bước lên ý tưởng đến khi có trọn bộ nguyên liệu hoàn chỉnh:
- **Trợ lý viết kịch bản thông minh (Gemini AI)**: Dựng khung kịch bản (Outline) từ chủ đề/thời lượng mục tiêu (60-180s), gợi ý đoạn tiếp theo, hoặc trau chuốt lại bản nháp theo phong cách audio narration lôi cuốn, có câu hook mạnh ở 5 giây đầu.
- **Tự động gắn nhịp điệu (Auto-Pace)**: Chèn các thẻ nhịp điệu kể chuyện (`[fast]`, `[slow]`, `[pause]`, `*emphasis*`, `[whisper]`) giúp giọng đọc trầm bổng, giữ chân người xem.
- **Bảng kiểm chứng sự thật & trích dẫn nguồn (Fact Check)**: Bóc tách từng luận điểm thực tế, phân loại chính xác thành 2 nhãn (**ĐÃ CHỨNG MINH** kèm link tài liệu uy tín / **CHƯA RÕ**), cho phép chỉnh sửa câu an toàn (Safe rewrite) hoặc ghi đè nhãn thủ công.
- **Tổng hợp giọng đọc chất lượng cao (TTS Engine)**:
  - Mặc định sử dụng giọng nam chuẩn tiếng Anh qua `edge-tts` (miễn phí, giọng đọc tự nhiên như người thật).
  - Tích hợp cơ chế **tự động fallback offline với Kokoro TTS**: khi mất mạng Internet, hệ thống tự động chuyển sang mô hình cục bộ mà không làm gián đoạn công việc.
  - Tự động chuẩn hóa âm lượng theo tiêu chuẩn phát thanh truyền hình **EBU R128 (-16 LUFS)**.
- **Tạo phụ đề chuẩn SRT (Subtitles)**: Trích xuất mốc thời gian chi tiết từng từ bằng `faster-whisper`, tự động nhóm thành từng cụm câu tự nhiên từ 5 đến 8 từ trên mỗi dòng phụ đề.
- **Xuất gói thành phẩm (Export Package)**: Xuất trực tiếp vào thư mục dự án gồm:
  1. `narration.mp3`: Giọng đọc hoàn chỉnh đã chèn khoảng lặng chuẩn và cân bằng âm lượng.
  2. `subtitles.srt`: File phụ đề chuẩn SRT để nạp vào CapCut, Premiere, DaVinci Resolve.
  3. `sources.txt`: Danh sách nguồn dẫn chứng được định dạng sẵn để dán ngay vào phần mô tả (Description) của YouTube.

---

## 2. Yêu cầu hệ thống & Cài đặt tiên quyết (Prerequisites)

1. **Hệ điều hành**: Windows 10 hoặc 11 (64-bit), tối thiểu 8 GB RAM (khuyến nghị 16 GB).
2. **Python**: Phiên bản **3.11** trở lên (Khuyến nghị Python 3.11 - 3.13).
   - Tải bộ cài chính thức tại: [python.org/downloads](https://www.python.org/downloads/)
   - *Lưu ý quan trọng*: Trong trình cài đặt, hãy tích chọn ô **"Add python.exe to PATH"**.
3. **FFmpeg** (Bắt buộc để ghép âm thanh, tạo khoảng lặng và chuẩn hóa loudness EBU R128):
   - Mở **PowerShell** hoặc Command Prompt trên Windows và chạy lệnh sau qua Windows Package Manager:
     ```powershell
     winget install Gyan.FFmpeg
     ```
   - Sau khi cài xong, mở một cửa sổ terminal mới và gõ lệnh sau để kiểm tra:
     ```powershell
     ffmpeg -version
     ```
     *(Hệ thống đã tích hợp sẵn cơ chế tự động quét tìm FFmpeg trong thư mục WinGet nên không cần cài đặt PATH thủ công).*
4. **Khóa Google Gemini API Key** (Miễn phí 100%):
   - Truy cập [Google AI Studio](https://aistudio.google.com/) và bấm **Get API key**.
   - Tạo một API key miễn phí mới và sao chép mã khóa.

---

## 3. Cấu hình môi trường

1. **Tạo file `.env`**:
   - Sao chép file `.env.example` thành file `.env` trong cùng thư mục (hoặc để `start.bat` tự tạo):
     ```cmd
     copy .env.example .env
     ```
   - Mở file `.env` bằng Notepad hoặc VS Code và dán khóa API của bạn:
     ```env
     GEMINI_API_KEY=AIzaSy...khoa_api_cua_ban_o_day
     ```
2. **Cấu hình tùy chọn trong `config.yaml`**:
   - `gemini.model`: Model AI xử lý kịch bản (mặc định: `gemini-flash-lite-latest` với dự phòng tự động sang `gemini-3.5-flash-lite`).
   - `tts.voice`: Giọng đọc nam tiếng Anh bị khóa cho kênh (mặc định: `en-US-ChristopherNeural`).
   - `tts.fallback_provider`: Nhà cung cấp offline dự phòng (mặc định: `kokoro`).
   - `pacing_presets`: Tùy chỉnh tốc độ đọc cơ sở và độ dài khoảng lặng mặc định (`mystery`, `hype`, `calm`).

---

## 4. Khởi chạy ứng dụng (Quick Start)

Chỉ cần **nhấp đúp chuột vào file `start.bat`** (hoặc chạy từ cửa sổ dòng lệnh):
```cmd
start.bat
```

File thực thi này sẽ tự động:
1. Tạo môi trường ảo Python (`venv`) nếu chưa tồn tại.
2. Cài đặt toàn bộ thư viện cần thiết từ `requirements.txt`.
3. Kiểm tra xem FFmpeg đã có trên máy hay chưa.
4. Tự động tạo file `.env` mẫu nếu bạn chưa có.
5. Khởi chạy máy chủ FastAPI và tự động mở trình duyệt web tại địa chỉ:
   ```
   http://127.0.0.1:8000
   ```

---

## 5. Hướng dẫn sử dụng chi tiết (Workflow)

### Bước 1: Quản lý dự án
- Bấm **+ Dự án mới** ở thanh bên trái (Sidebar).
- Đặt tiêu đề cho dự án ở góc trên bên trái. Hệ thống sẽ tự động lưu lại kịch bản (Autosave) sau mỗi vài giây khi bạn gõ.
- Mỗi dự án được lưu trữ riêng biệt tại `projects/<project_id>/project.json`.

### Bước 2: Soạn thảo hoặc sáng tạo kịch bản với Trợ lý Gemini AI
- **Dựng khung kịch bản (Dựng khung từ ý tưởng)**: Nhập chủ đề bạn muốn làm (ví dụ: *"Greenland sharks live 400 years"*), chọn thời lượng mục tiêu (60s - 180s). AI sẽ dựng ngay bản nháp hoàn chỉnh có hook, thân bài và cái kết bất ngờ.
- **Viết lại bản nháp (Viết lại bản nháp)**: Trau chuốt lại câu từ ngắn gọn, tăng tính tò mò, giữ trọn vẹn sự thật mà không bịa số liệu.
- **Gợi ý đoạn tiếp theo**: AI gợi ý 3 phương án viết tiếp từ vị trí hiện tại; bấm vào phương án ưng ý để chèn ngay vào kịch bản.

### Bước 3: Đặt nhịp điệu kể chuyện (Pacing Markup)
Bạn có thể tự gõ hoặc bấm nút **"⚡ Tự thêm nhịp"** để AI phân tích cấu trúc kịch bản và chèn nhịp tự động:
- `[fast]nội dung[/fast]`: Đọc nhanh hơn (+12%) cho câu mở đầu lôi cuốn hoặc chuỗi sự kiện dồn dập.
- `[slow]nội dung[/slow]`: Đọc chậm lại (-15%) khi chuẩn bị tiết lộ bí mật hoặc tình tiết hồi hộp.
- `[pause 0.5]`: Nghỉ đúng 0.5 giây (hoặc bất kỳ số giây nào như `[pause 1.0]`) trước khi đưa ra sự thật chấn động.
- `*từ ngữ*`: Nhấn giọng (emphasis), tăng nhẹ cao độ và âm lượng.
- `[whisper]nội dung[/whisper]`: Giọng thì thầm bí ẩn.
- Bấm **"🔊 Nghe thử"** bất cứ lúc nào để nghe thử đoạn văn bản đang bôi đen hoặc đoạn hiện tại.

### Bước 4: Bóc tách & Kiểm chứng sự thật (Fact Check)
- Mở bảng bên phải, bấm **"🔍 Bóc tách & Kiểm chứng"**.
- Hệ thống sẽ trích xuất từng luận điểm và phân loại:
  - **ĐÃ CHỨNG MINH** (Huy hiệu xanh lá): Đi kèm tóm tắt bằng chứng khoa học và liên kết tài liệu uy tín (Nature, Science, Wikipedia...).
  - **CHƯA RÕ** (Huy hiệu vàng): Những luận điểm chưa có cơ sở rõ ràng. Bạn có thể bấm **"🛡️ Sửa câu này cho an toàn"** để AI viết lại câu văn chính xác, tránh thông tin sai lệch.
- Có thể thêm liên kết nguồn tùy chỉnh bằng ô `+ Thêm link nguồn`, hoặc thay đổi nhãn thủ công theo ý muốn.

### Bước 5: Xuất Audio, Phụ đề & Nguồn tham khảo
- Bấm **"📦 Xuất Audio & Phụ đề"**.
- Nếu dự án còn luận điểm "CHƯA RÕ", hộp thoại cảnh báo an toàn sẽ xuất hiện nhắc nhở bạn xác nhận trước khi tiếp tục.
- Hệ thống thực hiện 3 bước:
  1. Tổng hợp giọng đọc TTS và ghép các đoạn khoảng lặng, chuẩn hóa âm lượng.
  2. Chạy `faster-whisper` trích xuất phụ đề và căn nhóm 5-8 từ mỗi dòng `.srt`.
  3. Tạo file `sources.txt` chứa toàn bộ tài liệu kiểm chứng.
- Khi hoàn tất, bạn có thể tải về trực tiếp từng file (`narration.mp3`, `subtitles.srt`, `sources.txt`) hoặc bấm **"📂 Mở thư mục dự án"** để lấy file đưa vào phần mềm dựng video.

---

## 6. Cấu hình giọng đọc Offline (Kokoro TTS Fallback)

Nếu bạn cần làm việc ở nơi không có kết nối Internet:
1. Tải 2 file mô hình Kokoro ONNX:
   - File trọng số mô hình: `kokoro-v0_19.onnx` (~300MB)
   - File giọng: `voices.json`
2. Tạo thư mục `assets/kokoro/` và đặt 2 file trên vào thư mục này:
   ```
   assets/
     kokoro/
       kokoro-v0_19.onnx
       voices.json
   ```
3. Khi mất kết nối mạng hoặc server EdgeTTS không phản hồi, hệ thống sẽ tự động chuyển sang đọc bằng Kokoro TTS offline với giọng nam đã cấu hình (`am_adam`, `bm_daniel`, ...).

---

## 7. Xử lý sự cố thường gặp (Troubleshooting)

- **Lỗi: 'python' is not recognized as an internal or external command**:
  - Gỡ và cài lại Python từ [python.org](https://www.python.org/downloads/), chú ý tích chọn ô **"Add python.exe to PATH"** ở màn hình cài đặt đầu tiên.
- **Thanh trạng thái báo đỏ: "⚠️ Thiếu FFmpeg"**:
  - Mở PowerShell và chạy lệnh: `winget install Gyan.FFmpeg`.
  - Khởi động lại ứng dụng bằng cách đóng cửa sổ dòng lệnh và chạy lại `start.bat`.
- **Thanh trạng thái báo vàng: "⚠️ Thiếu GEMINI_API_KEY"**:
  - Mở file `.env` và kiểm tra xem đã có dòng `GEMINI_API_KEY=AIzaSy...` hay chưa.
  - Đảm bảo không có dấu ngoặc kép hoặc khoảng trắng thừa quanh khóa API.
- **Lỗi: "Rate limit 429 / Quota exhausted" khi gọi Gemini**:
  - Hệ thống đã tích hợp cơ chế tự động thử lại (retry với exponential backoff). Nếu vẫn quá tải, bạn chỉ cần chờ khoảng 30 đến 60 giây để gói miễn phí của Google hồi phục lại hạn ngạch.
- **Lỗi: "open() got an unexpected keyword argument 'metadata_errors'" khi tạo SRT**:
  - Sự cố không tương thích giữa `av 14+` và `faster-whisper` đã được mã nguồn xử lý tự động qua bộ vá tương thích ngược trong `captions.py`.
- **Chạy kiểm thử toàn bộ hệ thống**:
  - Để kiểm tra toàn bộ 35 unit test và integration test, mở terminal trong thư mục dự án và chạy:
    ```powershell
    .\venv\Scripts\python.exe -m unittest discover tests
    ```
