# 📊 StreamPulse
### Automated YouTube Show Analytics Pipeline

**StreamPulse** là dự án Data Engineering xây dựng hệ thống ELT tự động nhằm thu thập, lưu trữ và phân tích sự tăng trưởng của các chương trình YouTube theo thời gian.

**Tech Stack:** Python · SQL · BigQuery · Google Compute Engine · Bash · Cron

> **Status:** MVP — Data Pipeline Implemented · Cloud Automation Configured · Dashboard In Progress

---

## 1. Business Problem

**Làm thế nào để tự động theo dõi và phân tích sự tăng trưởng của một chương trình YouTube bất kỳ?**

YouTube Data API cung cấp các chỉ số tích lũy tại thời điểm truy vấn nhưng không cung cấp trực tiếp lịch sử tăng trưởng hằng ngày của từng video.

Để trả lời các câu hỏi như:

- Chương trình đang có bao nhiêu lượt xem?
- Video nào tăng trưởng nhanh nhất?
- Lượt xem thay đổi như thế nào qua từng ngày?

Hệ thống cần **thu thập dữ liệu định kỳ, lưu lịch sử và chuyển đổi dữ liệu thành thông tin có thể phân tích**.

### Solution

StreamPulse cho phép nhập kênh và tên chương trình, tự động xác định video liên quan, thu thập thống kê và duy trì lịch sử theo ngày trong BigQuery.

---

## 2. System Design

```text
Google Compute Engine
         │
     Cron + Bash
         │
   Python Pipeline
         │
   YouTube Data API
         │
      Raw JSON
         │
     BigQuery RAW
         │
       BRONZE
         │
       STAGING
         │
       SILVER
         │
   Daily Snapshots
         │
   Analytics / Power BI
      (Planned)
```

### Data Flow

| Layer | Responsibility |
|---|---|
| Raw | Lưu dữ liệu JSON gốc |
| Bronze | Trích xuất JSON và chuyển đổi kiểu dữ liệu |
| Staging | Chuẩn hóa, loại trùng và chuẩn bị dữ liệu |
| Silver | Lưu dữ liệu phân tích và lịch sử thống kê |

**Pipeline execution:**

```bash
python main.py --channel "@VieChannelOfficial" --show "casimatna"
```

Mỗi lần thực thi được gắn `run_id` và thời điểm thu thập `collected_at` để hỗ trợ truy vết.

---

## 3. Engineering Decisions & Trade-offs

| Decision | Why? | Trade-off |
|---|---|---|
| **ELT thay vì ETL** | Giữ dữ liệu trước khi chuyển đổi, tận dụng SQL của BigQuery | Tăng số bảng trung gian và chi phí xử lý |
| **Raw JSON** | Hỗ trợ kiểm tra và xử lý lại dữ liệu | Tốn thêm dung lượng; khả năng replay phụ thuộc vào việc giữ Raw lịch sử |
| **Daily Snapshot** | Theo dõi tăng trưởng thay vì chỉ lưu số liệu mới nhất | Không khôi phục chính xác được ngày bỏ lỡ |
| **SQL MERGE** | Tránh trùng `(video_id, snapshot_date)` khi chạy lại | Cần xử lý trùng khóa ở nguồn trước khi MERGE |
| **Partition + Cluster** | Tối ưu các truy vấn theo ngày và video | Lợi ích phụ thuộc quy mô và cách truy vấn |
| **Cron thay vì Airflow** | Đủ cho pipeline nhỏ chạy theo lịch hằng ngày | Hạn chế về retry, backfill và monitoring |
| **BigQuery** | SQL analytics trên cloud, không cần quản trị database server | Chi phí truy vấn và phụ thuộc nền tảng cloud |

**Design principle:** Chọn giải pháp đơn giản nhất đáp ứng yêu cầu hiện tại, chỉ tăng độ phức tạp khi có nhu cầu thực tế.

---

## 4. Data Modeling & Incremental Processing

### `silver_youtube.fact_video_stats`

**Grain:** Một video có tối đa một snapshot mỗi ngày.

**Primary business key:** `(video_id, snapshot_date)`

Các chỉ số được lưu gồm `view_count`, `like_count`, `comment_count`, cùng `collected_at` và `run_id`.

**Storage design:**
- Partition: `snapshot_date`
- Cluster: `video_id`

**MERGE strategy:**
- **Ngày mới:** INSERT snapshot mới.
- **Cùng ngày:** UPDATE nếu `collected_at` mới hơn.
- **Chạy lại:** Không tạo thêm bản ghi trùng khóa.

Ví dụ:

| Date | Views | Growth |
|---|---:|---:|
| 01/11 | 100,000 | — |
| 02/11 | 125,000 | +25,000 |
| 03/11 | 148,000 | +23,000 |

Tăng trưởng được tính từ chênh lệch giữa các snapshot liên tiếp, không phải số lượt xem phát sinh chính xác trong từng ngày nếu lịch thu thập bị gián đoạn.

---

## 5. Deployment & Usage

**Requirements:** Python 3 · YouTube API Key · Google Cloud / BigQuery credentials

```bash
git clone <REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

Tạo `.env` với các biến môi trường mà pipeline yêu cầu, bao gồm API key.

**Run:**

```bash
bash run.sh
```

**Scheduling:** Pipeline được cấu hình chạy trên Google Compute Engine bằng Cron lúc **12:00 hằng ngày (UTC+7)**.

```cron
0 5 * * * /bin/bash /path/to/run.sh
```

*Biểu thức trên áp dụng khi máy ảo sử dụng múi giờ UTC. Việc thực thi tự động cần được xác nhận qua log và dữ liệu BigQuery.*

---

## 6. Limitations & Next Steps

**Current limitations**
- Nhận diện chương trình bằng từ khóa/hashtag, có thể sai hoặc bỏ sót.
- Không thể tái tạo chính xác snapshot của ngày không thu thập.
- Data quality checks, retry và monitoring chưa hoàn thiện.
- Dashboard chưa hoàn thành.

**Next steps**
1. Xác nhận Cron thực thi thành công và dữ liệu được cập nhật.
2. Xây dựng Power BI dashboard phân tích tăng trưởng.
3. Bổ sung ảnh kết quả và hoàn thiện tài liệu dự án.

---

**StreamPulse — Turning YouTube Data into Time-Series Insights.**
