# 📊 StreamPulse
### Hệ thống thu thập và phân tích dữ liệu YouTube tự động

**StreamPulse** là dự án Data Engineering xây dựng hệ thống ELT tự động bằng Python và Google BigQuery, nhằm thu thập, xử lý và lưu trữ dữ liệu thống kê video YouTube theo thời gian.

Hệ thống cho phép lựa chọn kênh YouTube và chương trình cần theo dõi, sau đó tự động thu thập dữ liệu, chuyển đổi thành các bảng có cấu trúc và lưu lịch sử thống kê hằng ngày để phục vụ phân tích tăng trưởng.

> **Trạng thái:** MVP — Phiên bản đầu tiên, đang tiếp tục phát triển và hoàn thiện.

---

## 1. Tổng quan dự án

### Bài toán

YouTube cung cấp các chỉ số như lượt xem, lượt thích và bình luận của video. Tuy nhiên, những chỉ số này chủ yếu phản ánh số liệu tích lũy tại thời điểm truy vấn.

Ví dụ:

| Ngày | Lượt xem |
|---|---:|
| 01/11/2026 | 1.000.000 |
| 02/11/2026 | 1.250.000 |
| 03/11/2026 | 1.400.000 |

Nếu chỉ lấy dữ liệu tại thời điểm hiện tại, chúng ta không thể xác định chính xác mức thay đổi giữa các lần thu thập trước đó.

### Giải pháp

StreamPulse xây dựng một pipeline dữ liệu nhằm:

- Tự động thu thập thông tin kênh và video thông qua YouTube Data API.
- Lọc các video liên quan đến chương trình được lựa chọn.
- Lưu dữ liệu gốc trước khi xử lý.
- Chuyển đổi dữ liệu JSON thành các bảng có cấu trúc trên BigQuery.
- Lưu lịch sử thống kê video theo từng ngày.
- Sử dụng SQL `MERGE` để cập nhật dữ liệu và hạn chế trùng lặp.
- Hỗ trợ tự động thực thi pipeline theo lịch bằng Cron Job.

---

## 2. Kiến trúc hệ thống

```text
                 CRON JOB
             (12:00 mỗi ngày)
                     |
                     v
                 BASH SCRIPT
                     |
                     v
                 PYTHON ELT
                     |
                     v
              YOUTUBE DATA API
                     |
                     v
                RAW JSON
                     |
                     v
              BIGQUERY RAW
                     |
                     v
             BIGQUERY BRONZE
                     |
                     v
               SQL STAGING
                     |
                     v
             BIGQUERY SILVER
                     |
                     v
             DAILY SNAPSHOTS
```

Hệ thống sử dụng kiến trúc ELT:

**Extract:** Thu thập dữ liệu từ YouTube API.

**Load:** Nạp dữ liệu vào Google BigQuery.

**Transform:** Sử dụng SQL để xử lý, chuẩn hóa và xây dựng các bảng phục vụ phân tích.

---

## 3. Công nghệ sử dụng

| Công nghệ | Vai trò |
|---|---|
| Python | Thu thập dữ liệu và điều phối pipeline |
| YouTube Data API v3 | Cung cấp thông tin kênh và video |
| Google BigQuery | Lưu trữ và xử lý dữ liệu |
| SQL | Chuyển đổi và cập nhật dữ liệu |
| Bash Script | Tự động thực thi các bước chạy |
| Cron Job | Lập lịch thu thập dữ liệu |
| Google Compute Engine | Máy ảo chạy pipeline trên cloud |
| Git & GitHub | Quản lý mã nguồn |

---

## 4. Quy trình xử lý dữ liệu

### 4.1. Extract — Thu thập dữ liệu

Pipeline nhận hai tham số đầu vào:

- `channel`: Kênh YouTube cần thu thập.
- `show`: Chương trình cần theo dõi.

Ví dụ:

```bash
python main.py \
    --channel "@VieChannelOfficial" \
    --show "casimatna"
```

Hệ thống sử dụng YouTube Data API để thu thập:

- Thông tin kênh YouTube.
- Danh sách video được đăng tải.
- Thông tin chi tiết của các video phù hợp.
- Các chỉ số thống kê của video.

Mỗi lần thực thi pipeline được gắn một `run_id` nhằm hỗ trợ theo dõi quá trình xử lý.

### 4.2. Raw — Lưu trữ dữ liệu gốc

Dữ liệu JSON được lưu lại trước khi thực hiện chuyển đổi.

Mục đích:

- Giữ lại dữ liệu phản hồi từ API.
- Hỗ trợ kiểm tra và xử lý lỗi.
- Tạo nguồn dữ liệu đầu vào cho các bước tiếp theo.

### 4.3. Bronze — Chuẩn hóa cấu trúc

Dữ liệu từ Raw được chuyển đổi thành các bảng có cấu trúc trong BigQuery.

Các trường dữ liệu được trích xuất từ JSON và chuyển sang kiểu dữ liệu phù hợp.

Ví dụ:

- `video_id`
- `channel_id`
- `video_title`
- `published_at`
- `description`

### 4.4. Staging — Chuẩn bị dữ liệu

Tầng Staging thực hiện các phép biến đổi SQL để chuẩn bị dữ liệu cho các bảng phân tích.

Các thao tác có thể bao gồm:

- Lựa chọn những trường dữ liệu cần thiết.
- Chuyển đổi kiểu dữ liệu.
- Chuẩn hóa thời gian thu thập.
- Chuẩn bị dữ liệu thống kê để thực hiện `MERGE`.

### 4.5. Silver — Lưu trữ dữ liệu phân tích

Tầng Silver chứa các bảng dữ liệu đã được xử lý để phục vụ phân tích.

Một trong những bảng chính là:

`silver_youtube.fact_video_stats`

Bảng này lưu lịch sử thống kê video theo ngày.

| Trường | Ý nghĩa |
|---|---|
| video_id | Mã định danh video |
| channel_id | Mã định danh kênh |
| snapshot_date | Ngày thu thập thống kê |
| view_count | Tổng lượt xem |
| like_count | Tổng lượt thích |
| comment_count | Tổng bình luận |
| favorite_count | Tổng lượt yêu thích |
| collected_at | Thời điểm thu thập |
| run_id | Mã lần chạy pipeline |

**Grain của bảng:** Một video có tối đa một bản ghi thống kê trong mỗi ngày.

Bảng được:

- Partition theo `snapshot_date`.
- Cluster theo `video_id`.

---

## 5. Cơ chế lưu lịch sử thống kê

StreamPulse sử dụng SQL `MERGE` để duy trì dữ liệu thống kê theo ngày.

### Khi pipeline chạy vào ngày mới

Hệ thống thêm bản ghi thống kê mới mà không xóa lịch sử ngày trước.

### Khi pipeline chạy lại trong cùng ngày

Nếu video đã có bản ghi trong ngày, hệ thống cập nhật dữ liệu khi `collected_at` của bản ghi mới lớn hơn bản ghi hiện tại.

Ví dụ:

| video_id | snapshot_date | view_count |
|---|---|---:|
| A001 | 01/11/2026 | 100.000 |
| A001 | 02/11/2026 | 125.000 |
| A001 | 03/11/2026 | 148.000 |

Từ lịch sử này, có thể tính toán:

- Mức tăng trưởng lượt xem giữa các lần thu thập.
- Mức thay đổi lượt thích và bình luận.
- Xu hướng phát triển của từng video.
- So sánh hiệu suất giữa các video hoặc chương trình.

Ví dụ SQL tính tăng trưởng:

```sql
SELECT
    video_id,
    snapshot_date,
    view_count,

    view_count - LAG(view_count) OVER (
        PARTITION BY video_id
        ORDER BY snapshot_date
    ) AS view_growth

FROM `youtube-pipeline-512201.silver_youtube.fact_video_stats`;
```

**Lưu ý:** Nếu thiếu dữ liệu một ngày, kết quả thể hiện mức thay đổi giữa hai lần thu thập liên tiếp, không nhất thiết là tăng trưởng trong đúng 24 giờ.

---

## 6. Hướng dẫn cài đặt và sử dụng

### Yêu cầu

- Python 3
- Tài khoản Google Cloud
- Google BigQuery
- YouTube Data API Key
- Quyền truy cập BigQuery phù hợp

### Bước 1: Clone repository

```bash
git clone <LINK_REPOSITORY>
cd <TEN_THU_MUC_PROJECT>
```

### Bước 2: Cấu hình môi trường

Tạo file `.env` và khai báo các biến môi trường mà project yêu cầu.

Ví dụ:

```env
YOUTUBE_API_KEY=your_api_key
```

Không đưa API key hoặc thông tin xác thực lên GitHub.

### Bước 3: Chạy pipeline

Trên Ubuntu:

```bash
bash run.sh
```

Bash Script hỗ trợ:

1. Tạo môi trường Python `.venv` nếu chưa tồn tại.
2. Cài đặt thư viện từ `requirements.txt`.
3. Thực thi `main.py` với các tham số đã cấu hình.

### Bước 4: Tự động hóa bằng Cron

Pipeline có thể được triển khai trên máy ảo Google Compute Engine và thực thi tự động hằng ngày.

Ví dụ:

```cron
0 5 * * *
```

Nếu máy ảo sử dụng múi giờ UTC, lịch này tương ứng với **12:00 trưa theo giờ Việt Nam**.

Máy ảo cần duy trì trạng thái hoạt động để Cron thực thi đúng lịch.

---

## 7. Những hạn chế hiện tại

Dự án đang trong giai đoạn MVP nên vẫn tồn tại một số hạn chế:

**Nhận diện chương trình**

Hệ thống sử dụng từ khóa trong tiêu đề và hashtag trong mô tả để xác định video thuộc chương trình được lựa chọn.

Phương pháp này có thể nhận diện nhầm hoặc bỏ sót một số video.

**Dữ liệu thống kê**

Các chỉ số từ YouTube API là dữ liệu tích lũy tại thời điểm thu thập, không phải dữ liệu sự kiện của từng lượt xem.

**Lịch sử dữ liệu**

Nếu pipeline không chạy trong một ngày, hệ thống có thể không có snapshot của ngày đó.

**Khả năng chịu lỗi**

Cơ chế kiểm thử, giám sát và khôi phục sau lỗi vẫn đang được tiếp tục phát triển.

---

## 8. Hướng phát triển

Các chức năng dự kiến bổ sung:

- Cải thiện độ chính xác khi nhận diện chương trình.
- Xây dựng dashboard phân tích tăng trưởng.
- Bổ sung kiểm tra chất lượng dữ liệu.
- Hoàn thiện cơ chế xử lý lỗi và chạy lại pipeline.
- Theo dõi trạng thái và thời gian thực thi.
- Bổ sung automated tests.
- Cải thiện khả năng xử lý dữ liệu từ nhiều kênh và chương trình.

---

## 9. Mục tiêu dự án

StreamPulse được xây dựng nhằm thực hành và phát triển các kỹ năng Data Engineering:

- Thiết kế pipeline ELT.
- Tích hợp và khai thác dữ liệu từ API.
- Xây dựng hệ thống lưu trữ dữ liệu trên cloud.
- Thiết kế mô hình dữ liệu phục vụ phân tích.
- Xử lý dữ liệu lịch sử theo thời gian.
- Tự động hóa quá trình thu thập dữ liệu.
- Tìm hiểu các nguyên tắc về độ tin cậy và khả năng bảo trì hệ thống.

Dự án được phát triển theo hướng từng bước hoàn thiện, từ một pipeline cơ bản đến một hệ thống dữ liệu có khả năng vận hành tự động.

---

**StreamPulse — Biến dữ liệu YouTube thành thông tin phân tích theo thời gian.**
