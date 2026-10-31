import logging
import time
from uuid import uuid4
from datetime import datetime, timezone
from elt.logging_config import setup_logging
from elt.youtube_client import get_youtube
from elt.channels_extraction import channel_information
from elt.storage import save_raw_json
from elt.bq_loader import load_to_bigquery
from elt.uploads_extraction import get_all_videos_id
from elt.bq_query import *
from elt.extract_video import get_video_static
from elt.arg_parser import arg_parse
import sys
logger = logging.getLogger(__name__)

PROJECT_ID = "youtube-pipeline-512201"
args = arg_parse()
channel = str(args.channel).replace("@","")
show = args.show
run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + "_"
        + uuid4().hex[:8]
    )
def main():
    setup_logging()
    start_time = time.perf_counter()
    
    
    
    logger.info("========== PIPELINE START ==========")
    logger.info("RUN ID: %s", run_id)
    logger.info(f"Channel: {channel}")
    logger.info(f"Show: {show}")
    try:
        data = channel_information(channel=channel)
        save_raw_json(filename="channels.json",data=data,run_id=run_id)
        load_to_bigquery(file_name=f"channels.json",project_id=PROJECT_ID,dataset_id="raw_youtube",table_id=f"raw_channels")
        sql_query(project_id=PROJECT_ID,filename="bronze_channels.sql")
        data = sql_query(project_id=PROJECT_ID,filename="extract_uploads_id.sql")
        data = get_all_videos_id(uploads_id=data)
        save_raw_json(filename="uploads.json",data=data,run_id=run_id)
        load_to_bigquery(file_name="uploads.json",project_id=PROJECT_ID,dataset_id="raw_youtube",table_id="raw_uploads")
        sql_query(project_id=PROJECT_ID,filename="bronze_uploads.sql")
        data =  sql_query_filter(project_id=PROJECT_ID,filename="extract_filtered_video_ids.sql",show=show)
        statictis_videos = []
        logger.info("Bắt đầu lấy dữ liệu videos ")
        for item in data:
            statistic = get_video_static(video_id=item)
            statictis_videos.append(statistic)
        save_raw_json(filename="videos_statistic.json",data = statictis_videos,run_id=run_id)
        load_to_bigquery(file_name="videos_statistic.json",project_id=PROJECT_ID,dataset_id="raw_youtube",table_id="raw_video_statistics")
        sql_query(project_id=PROJECT_ID,filename="bronze_videos_detail.sql")
        sql_query(project_id=PROJECT_ID,filename="stg_dim_channels.sql")
        sql_query(project_id=PROJECT_ID,filename="stg_fact_channels.sql")
        sql_query(project_id=PROJECT_ID,filename="stg_dim_videos.sql")
        sql_query(project_id=PROJECT_ID,filename="stg_fact_videos.sql")
        sql_query(project_id=PROJECT_ID,filename="silver_dim_channels.sql")
        sql_query(project_id=PROJECT_ID,filename="silver_fact_channels.sql")
        sql_query(project_id=PROJECT_ID,filename="silver_dim_videos.sql")
        sql_query(project_id=PROJECT_ID,filename="silver_fact_videos.sql")
    except ValueError:
        logging.error(f"Lỗi: {ValueError}")

    else:
        elapsed = time.perf_counter() - start_time

        logger.info(
            "PIPELINE FINISHED | run_id=%s | duration=%.2f seconds",
            run_id,
            elapsed
        )


if (__name__) == "__main__":
    main()

