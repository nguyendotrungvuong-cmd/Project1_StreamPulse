CREATE OR REPLACE TABLE
`youtube-pipeline-512201.staging_youtube.stg_dim_videos`
AS

SELECT
    video_id,
    channel_id,
    channel_title,
    video_title,
    description,
    published_at,
    category_id,
    default_language,
    thumbnail_url,
    tags,
    collected_at,
    run_id

FROM `youtube-pipeline-512201.bronze_youtube.bronze_videos_statistics`

WHERE video_id IS NOT NULL

QUALIFY ROW_NUMBER() OVER (
    PARTITION BY video_id
    ORDER BY collected_at DESC, run_id DESC
) = 1;