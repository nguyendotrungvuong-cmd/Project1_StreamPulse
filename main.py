import logging
import time
from uuid import uuid4
from datetime import datetime, timezone

from elt.youtube_client import get_youtube
from elt.channels_extraction import channel_information
from elt.storage import save_raw_json
from elt.bq_loader import load_to_bigquery
from elt.uploads_extraction import get_all_videos_id
from elt.bq_query import *
from elt.extract_video import get_video_static


# =========================
# LOGGING CONFIG
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)

PROJECT_ID = "youtube-pipeline-512201"


def main():

    start_time = time.perf_counter()

    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        + "_"
        + uuid4().hex[:8]
    )

    logger.info("========== PIPELINE START ==========")
    logger.info("RUN ID: %s", run_id)

    try:

        # =========================
        # 1. CHANNEL EXTRACTION
        # =========================

        logger.info("[1/5] CHANNEL EXTRACTION START")

        channels_data_json = channel_information(
            channel="@VieChannelOfficial"
        )

        save_raw_json(
            filename="channels",
            data=channels_data_json,
            run_id=run_id
        )

        load_to_bigquery(
            file_name="channels",
            project_id=PROJECT_ID,
            dataset_id="raw_youtube",
            table_id="channels"
        )

        bronze_channels(project_id=PROJECT_ID)

        logger.info("[1/5] CHANNEL EXTRACTION SUCCESS")

        # =========================
        # 2. UPLOADS EXTRACTION
        # =========================

        logger.info("[2/5] UPLOADS EXTRACTION START")

        playlist_id = extract_uploads_id(
            project_id=PROJECT_ID
        )

        logger.info("Playlist ID: %s", playlist_id)

        data = get_all_videos_id(
            uploads_id=playlist_id
        )

        save_raw_json(
            filename="uploads",
            data=data,
            run_id=run_id
        )

        load_to_bigquery(
            file_name="uploads",
            project_id=PROJECT_ID,
            dataset_id="raw_youtube",
            table_id="uploads"
        )

        bronze_uploads(project_id=PROJECT_ID)

        logger.info("[2/5] UPLOADS EXTRACTION SUCCESS")

        # =========================
        # 3. VIDEO EXTRACTION
        # =========================

        logger.info("[3/5] VIDEO EXTRACTION START")

        video_ids = extract_filtered_video_ids(
            project_id=PROJECT_ID
        )

        logger.info("Total videos: %s", len(video_ids))

        response = []

        for index, video_id in enumerate(video_ids, start=1):

            logger.info(
                "Extracting video %s/%s | video_id=%s",
                index,
                len(video_ids),
                video_id
            )

            static = get_video_static(video_id=video_id)

            response.append(static)

        save_raw_json(
            filename="video_statistic",
            data=response,
            run_id=run_id
        )

        load_to_bigquery(
            file_name="video_statistic",
            project_id=PROJECT_ID,
            dataset_id="raw_youtube",
            table_id="video_details"
        )

        bronze_video_details(project_id=PROJECT_ID)

        logger.info("[3/5] VIDEO EXTRACTION SUCCESS")

        # =========================
        # 4. STAGING
        # =========================

        logger.info("[4/5] STAGING START")

        stg_dim_channels(project_id=PROJECT_ID)
        logger.info("STAGING DIM CHANNELS SUCCESS")

        stg_fact_channels(project_id=PROJECT_ID)
        logger.info("STAGING FACT CHANNELS SUCCESS")

        stg_dim_videos(project_id=PROJECT_ID)
        logger.info("STAGING DIM VIDEOS SUCCESS")

        stg_fact_videos(project_id=PROJECT_ID)
        logger.info("STAGING FACT VIDEOS SUCCESS")

        logger.info("[4/5] STAGING SUCCESS")

        # =========================
        # 5. SILVER
        # =========================

        logger.info("[5/5] SILVER START")

        silver_dim_channels(project_id=PROJECT_ID)
        logger.info("SILVER DIM CHANNELS SUCCESS")

        silver_fact_channels(project_id=PROJECT_ID)
        logger.info("SILVER FACT CHANNELS SUCCESS")

        silver_dim_videos(project_id=PROJECT_ID)
        logger.info("SILVER DIM VIDEOS SUCCESS")

        silver_fact_videos(project_id=PROJECT_ID)
        logger.info("SILVER FACT VIDEOS SUCCESS")

        logger.info("[5/5] SILVER SUCCESS")

    except Exception:

        logger.exception(
            "PIPELINE FAILED | run_id=%s",
            run_id
        )

        raise

    else:

        logger.info(
            "PIPELINE SUCCESS | run_id=%s",
            run_id
        )

    finally:

        elapsed = time.perf_counter() - start_time

        logger.info(
            "PIPELINE FINISHED | run_id=%s | duration=%.2f seconds",
            run_id,
            elapsed
        )


if __name__ == "__main__":
    main()