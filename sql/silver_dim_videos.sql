CREATE TABLE IF NOT EXISTS
`youtube-pipeline-512201.silver_youtube.dim_videos`
(
    video_id STRING,
    channel_id STRING,
    channel_title STRING,
    video_title STRING,
    description STRING,
    published_at TIMESTAMP,
    category_id STRING,
    default_language STRING,
    thumbnail_url STRING,
    tags ARRAY<STRING>,
    collected_at TIMESTAMP,
    run_id STRING
);

MERGE `youtube-pipeline-512201.silver_youtube.dim_videos` AS target
USING `youtube-pipeline-512201.staging_youtube.stg_dim_videos` AS source

ON target.video_id = source.video_id

WHEN MATCHED
    AND (
        target.collected_at IS NULL
        OR source.collected_at > target.collected_at
    )
THEN UPDATE SET
    channel_id = source.channel_id,
    channel_title = source.channel_title,
    video_title = source.video_title,
    description = source.description,
    published_at = source.published_at,
    category_id = source.category_id,
    default_language = source.default_language,
    thumbnail_url = source.thumbnail_url,
    tags = source.tags,
    collected_at = source.collected_at,
    run_id = source.run_id

WHEN NOT MATCHED THEN
INSERT (
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
)
VALUES (
    source.video_id,
    source.channel_id,
    source.channel_title,
    source.video_title,
    source.description,
    source.published_at,
    source.category_id,
    source.default_language,
    source.thumbnail_url,
    source.tags,
    source.collected_at,
    source.run_id
);