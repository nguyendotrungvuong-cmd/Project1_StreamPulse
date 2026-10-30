CREATE TABLE IF NOT EXISTS
`youtube-pipeline-512201.silver_youtube.dim_channels`
(
    channel_id STRING,
    channel_title STRING,
    description STRING,
    custom_url STRING,
    country STRING,
    published_at TIMESTAMP,
    uploads_playlist_id STRING,
    collected_at TIMESTAMP,
    run_id STRING
);

MERGE `youtube-pipeline-512201.silver_youtube.dim_channels` AS target
USING `youtube-pipeline-512201.staging_youtube.stg_dim_channels` AS source

ON target.channel_id = source.channel_id

WHEN MATCHED
    AND (
        target.collected_at IS NULL
        OR source.collected_at > target.collected_at
    )
THEN UPDATE SET
    channel_title = source.channel_title,
    description = source.description,
    custom_url = source.custom_url,
    country = source.country,
    published_at = source.published_at,
    uploads_playlist_id = source.uploads_playlist_id,
    collected_at = source.collected_at,
    run_id = source.run_id

WHEN NOT MATCHED THEN
INSERT (
    channel_id,
    channel_title,
    description,
    custom_url,
    country,
    published_at,
    uploads_playlist_id,
    collected_at,
    run_id
)
VALUES (
    source.channel_id,
    source.channel_title,
    source.description,
    source.custom_url,
    source.country,
    source.published_at,
    source.uploads_playlist_id,
    source.collected_at,
    source.run_id
);