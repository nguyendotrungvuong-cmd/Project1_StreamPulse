from pathlib import Path
from google.cloud import bigquery
import logging
from elt.logging_config import setup_logging
ROOT = Path(__file__).resolve().parent.parent
SQL_PATH = ROOT / "sql"
setup_logging()
logger = logging.getLogger(__name__)
def extract_video_ids(project_id, show_name):
    client = bigquery.Client(project=project_id)

    # Đọc SQL từ file riêng
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "extract_video_ids.sql"

    sql = sql_path.read_text(encoding="utf-8")

    # Cho phép nhập tên show bất kỳ
    show_name = show_name.strip()

    if not show_name:
        raise ValueError("Tên show không được để trống")

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("show_name", "STRING", show_name)
        ]
    )

    query_job = client.query(sql, job_config=job_config)

    return [
        {
            "video_id": row.video_id,
            "video_title": row.video_title,
            "channel_name": row.channel_name,
            "channel_id": row.channel_id,
            "published_at": row.published_at,
        }
        for row in query_job.result()
    ]


def bronze_channels(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "bronze_channels.sql"
    sql = sql_path.read_text(encoding="utf-8")
    query = sql
    job = client.query(sql)
    job.result()


def bronze_uploads(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "bronze_uploads.sql"
    sql = sql_path.read_text(encoding="utf-8")
    query = sql
    job = client.query(sql)
    job.result()


def extract_uploads_id(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "extract_uploads_id.sql"
    sql = sql_path.read_text(encoding="utf-8")
    query = sql
    job = client.query(sql)
    rows = job.result()
    return [row.uploads_playlist_id for row in rows]


def extract_filtered_video_ids(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = (
        Path(__file__).resolve().parent.parent
        / "sql"
        / "extract_filtered_video_ids.sql"
    )
    sql = sql_path.read_text(encoding="utf-8")
    query = sql
    job = client.query(query=query)
    rows = job.result()
    return [row.video_id for row in rows]


def bronze_video_details(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = (
        Path(__file__).resolve().parent.parent / "sql" / "bronze_video_details.sql"
    )
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(query=sql)
    job.result()


def stg_dim_channels(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "stg_dim_channels.sql"
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(sql)
    job.result()


def stg_fact_channels(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "stg_fact_channels.sql"
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(sql)
    job.result()


def stg_dim_videos(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "stg_dim_videos.sql"
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(sql)
    job.result()


def stg_fact_videos(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "stg_fact_videos.sql"
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(sql)
    job.result()


def silver_dim_channels(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = (
        Path(__file__).resolve().parent.parent / "sql" / "silver_dim_channels.sql"
    )
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(sql)
    job.result()


def silver_fact_channels(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = (
        Path(__file__).resolve().parent.parent / "sql" / "silver_fact_channels.sql"
    )
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(sql)
    job.result()


def silver_dim_videos(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "silver_dim_videos.sql"
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(sql)
    job.result()


def silver_fact_videos(project_id):
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / "silver_fact_videos.sql"
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(sql)
    job.result()
def sql_query(project_id,filename):
    logger.info(f"Đang khởi tạo truy vấn SQL: {filename}")
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / f"{filename}"
    if not sql_path:
        raise ValueError(f"Lỗi: {ValueError}")
    sql = sql_path.read_text(encoding="utf-8")
    job = client.query(sql)
    job.result()
    rows = job.result()
    logger.info(f"Truy vấn SQL thành công: {filename}")
    return [row.uploads_playlist_id for row in rows]

def sql_query_filter(project_id,filename,show):
    logger.info(f"Đang khởi tạo truy vấn SQL: {filename}")
    client = bigquery.Client(project=project_id)
    sql_path = Path(__file__).resolve().parent.parent / "sql" / f"{filename}"
    if not sql_path:
        raise ValueError(f"Lỗi: {ValueError}")
    sql = sql_path.read_text(encoding="utf-8")
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
        bigquery.ScalarQueryParameter("show", "STRING", show)
        ]
    )
    job = client.query(sql,job_config=job_config)
    rows = job.result()
    logger.info(f"Truy vấn SQL thành công: {filename}")
    data = [row.video_id for row in rows]
    logger.info(f"Đã lọc xong: {len(data)} video ")
    return data