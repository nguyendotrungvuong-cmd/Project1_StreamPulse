import json
from pathlib import Path
from datetime import datetime, timezone
from google.cloud import bigquery
import logging

logger = logging.getLogger(__name__)


def load_to_bigquery(file_name, project_id, dataset_id, table_id):
    
        logger.info(
            f"Bắt đầu load {file_name} vào {project_id}.{dataset_id}.{table_id}"
        )
        client = bigquery.Client(project=project_id)

        # 1. Đường dẫn file Raw JSON
        raw_dir = Path("data/raw")
        file_path = raw_dir / f"{file_name}"

        full_table_id = f"{project_id}.{dataset_id}.{table_id}"

        # 2. Đọc JSON gốc
        with file_path.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)
        if not file_path:
             raise ValueError(f"Không tìm thấy đường dẫn: {file_path}")
        # 3. Chuẩn bị record
        rows = [
            {
                "batch_id": file_name,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                # QUAN TRỌNG: Giữ nguyên dictionary
                "payload": raw_data,
            }
        ]

      
        job_config = bigquery.LoadJobConfig(
            schema=[
                bigquery.SchemaField("batch_id", "STRING"),
                bigquery.SchemaField("collected_at", "TIMESTAMP"),
                bigquery.SchemaField("payload", "JSON"),
            ],
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )

   
        job = client.load_table_from_json(rows, full_table_id, job_config=job_config)

        # 6. Chờ hoàn thành
        job.result()

        # 7. Kiểm tra kết quả
        table = client.get_table(full_table_id)
      
        logger.info(f"Tổng số dòng: {table.num_rows}")
        logger.info(
            f"Đã load thành công {file_name} vào {project_id}.{dataset_id}.{table_id} "
        )
        logger.info(f"Tổng số dòng: {table.num_rows}")
        return table.num_rows


def load_ndjson(project_id, dataset_id, table_id, file_path):
    client = bigquery.Client(project=project_id)

    full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=[
            bigquery.SchemaField("collected_at", "TIMESTAMP"),
            bigquery.SchemaField("payload", "JSON"),
        ],
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    with open(file_path, "rb") as f:
        job = client.load_table_from_file(f, full_table_id, job_config=job_config)

    job.result()

    print(f"Load thành công: {full_table_id}")
