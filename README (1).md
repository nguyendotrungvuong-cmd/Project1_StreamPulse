# YouTube Channel Analytics Pipeline

> **Trạng thái:** Đang phát triển (demo pipeline ELT)

## 1. Giới thiệu

Dự án xây dựng pipeline **ELT (Extract – Load – Transform)** thu thập dữ liệu kênh và video từ **YouTube Data API**, lưu trữ và xử lý bằng **Google BigQuery**. Dữ liệu sau xử lý phục vụ phân tích hiệu suất và tăng trưởng lượt xem, người đăng ký và tương tác theo thời gian; **Power BI** là công cụ trực quan hóa dự kiến.

**Phạm vi demo hiện tại:** thu thập dữ liệu từ kênh `@VieChannelOfficial`, bóc tách thông tin kênh, danh sách video và thống kê video, sau đó xử lý qua các tầng RAW → BRONZE → STAGING → SILVER.

## 2. Mục tiêu

- Tự động thu thập metadata và các chỉ số thống kê từ YouTube.
- Xây dựng quy trình ELT có các tầng dữ liệu rõ ràng.
- Gắn `run_id` và `collected_at` để truy vết các lần chạy.
- Lưu **thông tin mới nhất** của kênh/video trong các bảng dimension.
- Lưu **snapshot thống kê theo ngày** trong các bảng fact để phân tích tăng trưởng.
- Chuẩn bị dữ liệu cho dashboard Power BI.

## 3. Kiến trúc hệ thống

```text
YouTube Data API
       │
       ▼
Python Extraction
       │
       ▼
RAW (JSON payload + run_id + collected_at)
       │
       ▼
BRONZE (bóc tách JSON thành các cột có cấu trúc)
       │
       ▼
STAGING (chuẩn hóa, loại trùng, chuẩn bị dữ liệu)
       │
       ▼
SILVER (DIM: metadata mới nhất | FACT: snapshot theo ngày)
       │
       ▼
Power BI (dự kiến: báo cáo tăng trưởng và hiệu suất)
```

### Vai trò từng tầng

| Tầng | Chức năng |
|---|---|
| **RAW** | Lưu phản hồi API dạng JSON và metadata của lần chạy. |
| **BRONZE** | Trích xuất trường dữ liệu từ JSON thành bảng có cấu trúc. |
| **STAGING** | Chuẩn hóa dữ liệu, chọn bản ghi phù hợp và loại trùng theo logic từng bảng. |
| **SILVER** | Cung cấp các bảng dimension và fact cho phân tích. |

> **Lưu ý về thiết kế hiện tại:** Các bảng fact trong Silver sử dụng khóa `(entity_id, snapshot_date)`, nghĩa là mỗi kênh/video giữ **một snapshot mới nhất trong ngày**, không phải một dòng cho mọi lần pipeline chạy. Nếu chạy nhiều lần cùng ngày, snapshot mới hơn có thể cập nhật dòng của ngày đó.

## 4. Công nghệ

| Công nghệ | Vai trò |
|---|---|
| **Python** | Gọi API, điều phối các bước ELT, ghi log. |
| **YouTube Data API** | Nguồn dữ liệu kênh, video và thống kê. |
| **Google BigQuery** | Lưu trữ và xử lý dữ liệu bằng SQL. |
| **SQL** | Bóc tách JSON, tạo staging, `MERGE` vào Silver. |
| **Power BI** | Trực quan hóa và phân tích (giai đoạn tiếp theo). |
| **Python logging** | Theo dõi tiến trình và lỗi pipeline. |

## 5. Mô hình dữ liệu Silver

| Bảng | Grain / khóa nghiệp vụ | Nội dung |
|---|---|---|
| `silver_youtube.dim_channels` | Một dòng / `channel_id` | Metadata mới nhất của kênh. |
| `silver_youtube.dim_videos` | Một dòng / `video_id` | Metadata mới nhất của video. |
| `silver_youtube.fact_channel_stats` | Một dòng / (`channel_id`, `snapshot_date`) | Số người đăng ký, lượt xem và số video theo ngày. |
| `silver_youtube.fact_video_stats` | Một dòng / (`video_id`, `snapshot_date`) | Lượt xem, lượt thích và bình luận theo ngày. |

**Quy tắc cập nhật:**

- **Dimension:** `MERGE` theo ID; thêm thực thể mới hoặc cập nhật metadata khi `collected_at` mới hơn.
- **Fact:** `MERGE` theo ID + ngày; thêm ngày chưa có hoặc cập nhật snapshot mới nhất của cùng ngày.
- **Không dùng TRUNCATE ở Silver:** Những ngày trước vẫn được giữ nếu đã được nạp thành công.

### Ví dụ tính tăng trưởng lượt xem

```sql
SELECT
    video_id,
    snapshot_date,
    view_count,
    view_count - LAG(view_count) OVER (
        PARTITION BY video_id
        ORDER BY snapshot_date
    ) AS view_growth
FROM `youtube-pipeline-512201.silver_youtube.fact_video_stats`
ORDER BY video_id, snapshot_date;
```

> Giá trị `view_growth` là chênh lệch giữa **hai ngày có snapshot liên tiếp**. Nếu thiếu ngày thu thập, đó không nhất thiết là tăng trưởng trong đúng một ngày.

## 6. Quy trình chạy pipeline

Các bước chính được điều phối trong `main.py`:

1. Sinh `run_id` cho lần chạy.
2. Lấy thông tin kênh và lưu vào RAW/BRONZE.
3. Lấy uploads playlist và danh sách video.
4. Thu thập chi tiết/thống kê video và lưu vào RAW/BRONZE.
5. Chạy các câu SQL tạo bảng STAGING.
6. `MERGE` dữ liệu từ STAGING sang bốn bảng SILVER.
7. Ghi log tiến trình và lỗi (nếu có).

### Cấu trúc thư mục chính

```text
channel-analytic/
├── main.py
├── elt/
│   ├── youtube_client.py
│   ├── channels_extraction.py
│   ├── uploads_extraction.py
│   ├── extract_video.py
│   ├── storage.py
│   ├── bq_loader.py
│   └── bq_query.py
├── sql/
│   └── ...                   # SQL Bronze, Staging, Silver
├── data/
│   └── raw/                  # Dữ liệu thu thập cục bộ (nếu có)
└── logs/
    └── pipeline.log         # Nếu cấu hình logging theo thư mục logs/
```

> Tên file SQL cụ thể phụ thuộc phiên bản mã nguồn hiện tại. Sơ đồ trên chỉ thể hiện các thành phần chính, không khẳng định đầy đủ mọi file trong repository.

## 7. Hướng dẫn cài đặt và chạy demo

### Bước 1 — Lấy mã nguồn và mở thư mục dự án

```bash
git clone <LINK_REPOSITORY>
cd channel-analytic
```

Nếu đã có mã nguồn trên máy, chỉ cần mở terminal tại thư mục chứa `main.py`. Thay `<LINK_REPOSITORY>` bằng địa chỉ repository thực tế khi công bố.

### Bước 2 — Tạo môi trường Python

**Linux / WSL / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Bước 3 — Cài thư viện

Nếu repository có `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

Nếu chưa có file này, cần tạo từ môi trường đang chạy được trên máy phát triển và kiểm tra lại trước khi chia sẻ. Ví dụ:

```bash
python -m pip freeze > requirements.txt
```

> Không nên coi `pip freeze` là danh sách dependencies đã được tối ưu; nó có thể bao gồm các gói không dùng tới.

### Bước 4 — Cấu hình YouTube API và Google Cloud

1. Chuẩn bị **YouTube Data API v3 key** và cấu hình theo cách mà `elt/youtube_client.py` đang đọc khóa. **Không commit API key vào GitHub.**
2. Chuẩn bị Google Cloud project có BigQuery và tài khoản/service account có quyền chạy query, tạo và cập nhật bảng.
3. Xác thực BigQuery bằng **một** trong các cách phù hợp:

**Cách A — Google Cloud CLI (dùng trên máy cá nhân):**

```bash
gcloud auth application-default login
```

**Cách B — Service account JSON (khi được cấp riêng):**

```bash
# Linux / WSL / macOS
export GOOGLE_APPLICATION_CREDENTIALS="/duong-dan/service-account.json"
```

```powershell
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\duong-dan\service-account.json"
```

> Tuyệt đối không đưa file service account JSON lên repository. Để giảng viên chạy trên máy riêng, cần cấp quyền và cấu hình thông tin xác thực riêng; mã nguồn không tự cung cấp quyền truy cập project của tác giả.

### Bước 5 — Kiểm tra BigQuery

Project đang cấu hình trong `main.py`:

```python
PROJECT_ID = "youtube-pipeline-512201"
```

Các dataset cần có trong project:

```text
raw_youtube
bronze_youtube
staging_youtube
silver_youtube
```

Các dataset phải được tạo trước nếu mã nguồn không có bước tự tạo. Nếu chạy bằng project khác, cập nhật **cả** `PROJECT_ID` trong Python và các tham chiếu project viết trực tiếp trong file `sql/*.sql`.

### Bước 6 — Chạy pipeline

Từ thư mục gốc, sau khi kích hoạt môi trường ảo:

```bash
python main.py
```

Pipeline thực hiện tuần tự: thu thập thông tin kênh → lấy danh sách video → lấy thống kê video → ghi RAW/BRONZE → tạo STAGING → MERGE vào SILVER.

**Theo dõi log:** Nếu đang sử dụng phiên bản `main.py` đã cấu hình logging, tiến trình được in ra terminal và ghi vào `logs/pipeline.log` (hoặc `pipeline.log` ở thư mục làm việc nếu chưa đổi đường dẫn). Có thể xem log trên Linux/WSL:

```bash
tail -f logs/pipeline.log
```

### Bước 7 — Kiểm tra kết quả trên BigQuery

**Kiểm tra số dòng của bốn bảng Silver:**

```sql
SELECT 'dim_channels' AS table_name, COUNT(*) AS total_rows
FROM `youtube-pipeline-512201.silver_youtube.dim_channels`
UNION ALL
SELECT 'fact_channel_stats', COUNT(*)
FROM `youtube-pipeline-512201.silver_youtube.fact_channel_stats`
UNION ALL
SELECT 'dim_videos', COUNT(*)
FROM `youtube-pipeline-512201.silver_youtube.dim_videos`
UNION ALL
SELECT 'fact_video_stats', COUNT(*)
FROM `youtube-pipeline-512201.silver_youtube.fact_video_stats`;
```

**Kiểm tra snapshot thống kê video theo ngày:**

```sql
SELECT
    snapshot_date,
    COUNT(DISTINCT video_id) AS total_videos
FROM `youtube-pipeline-512201.silver_youtube.fact_video_stats`
GROUP BY snapshot_date
ORDER BY snapshot_date DESC;
```

**Thử tính tăng trưởng khi đã có ít nhất hai ngày dữ liệu:**

```sql
SELECT
    video_id,
    snapshot_date,
    view_count,
    view_count - LAG(view_count) OVER (
        PARTITION BY video_id ORDER BY snapshot_date
    ) AS view_growth
FROM `youtube-pipeline-512201.silver_youtube.fact_video_stats`
ORDER BY video_id, snapshot_date;
```

### Lỗi thường gặp

- **`Required parameter is missing: query`**: kiểm tra file SQL được Python đọc có rỗng/chưa lưu hay không.
- **`403 Access Denied`**: tài khoản đang xác thực chưa đủ quyền BigQuery hoặc chưa được cấp quyền project.
- **Không có lịch sử tăng trưởng**: nếu chỉ chạy trong một ngày, bảng FACT hiện tại chỉ có một snapshot/ngày cho mỗi thực thể; cần dữ liệu của ít nhất hai ngày.
- **Chạy lại nhưng số dòng không tăng**: `MERGE` theo ID + ngày sẽ cập nhật dòng cùng ngày thay vì thêm dòng mới.

## 8. Kịch bản demo cho giảng viên

1. **Giới thiệu bài toán:** Vì sao cần lưu snapshot thống kê để phân tích tăng trưởng YouTube.
2. **Trình bày kiến trúc:** Luồng YouTube API → RAW → BRONZE → STAGING → SILVER.
3. **Chạy `main.py`:** Quan sát các bước thu thập và xử lý qua terminal/log.
4. **Mở BigQuery:** Kiểm tra dữ liệu đã được nạp vào các bảng.
5. **Giải thích `MERGE`:** DIM cập nhật metadata mới nhất; FACT giữ snapshot theo ngày.
6. **Chạy SQL tăng trưởng:** Minh họa `LAG()` khi có ít nhất hai ngày snapshot cho cùng video.
7. **Nêu hướng phát triển:** Dashboard Power BI, kiểm tra chất lượng dữ liệu và cơ chế khôi phục pipeline.

## 9. Giới hạn hiện tại và hướng phát triển

- **Dữ liệu tăng trưởng:** Cần ít nhất hai ngày có snapshot để tính chênh lệch theo ngày.
- **Độ chi tiết:** Thiết kế fact hiện tại không giữ tất cả các lần thu thập trong cùng một ngày.
- **Độ tin cậy:** Pipeline cần bổ sung kiểm tra batch đầy đủ trước khi nạp Silver và chiến lược retry/idempotency nhất quán.
- **RAW:** Cần kiểm tra cấu hình ghi dữ liệu (`WRITE_APPEND` hay `WRITE_TRUNCATE`) trước khi khẳng định RAW giữ toàn bộ lịch sử.
- **Trực quan hóa:** Xây dựng dashboard Power BI khi dữ liệu lịch sử đủ dài.

---

**Ghi chú:** Đây là README cho **bản demo đang phát triển**, không phải tài liệu xác nhận hệ thống đã vận hành production.
