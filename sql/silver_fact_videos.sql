CREATE TABLE IF NOT EXISTS
`youtube-pipeline-512201.silver_youtube.fact_video_stats`
(
    video_id STRING,
    channel_id STRING,
    snapshot_date DATE,
    view_count INT64,
    like_count INT64,
    comment_count INT64,
    favorite_count INT64,
    collected_at TIMESTAMP,
    run_id STRING
)
PARTITION BY snapshot_date
CLUSTER BY video_id;

MERGE `youtube-pipeline-512201.silver_youtube.fact_video_stats` AS target
USING `youtube-pipeline-512201.staging_youtube.stg_fact_video_stats` AS source

ON target.video_id = source.video_id
AND target.snapshot_date = source.snapshot_date

WHEN MATCHED
    AND (
        target.collected_at IS NULL
        OR source.collected_at > target.collected_at
    )
THEN UPDATE SET
    channel_id = source.channel_id,
    view_count = source.view_count,
    like_count = source.like_count,
    comment_count = source.comment_count,
    favorite_count = source.favorite_count,
    collected_at = source.collected_at,
    run_id = source.run_id

WHEN NOT MATCHED THEN
INSERT (
    video_id,
    channel_id,
    snapshot_date,
    view_count,
    like_count,
    comment_count,
    favorite_count,
    collected_at,
    run_id
)
VALUES (
    source.video_id,
    source.channel_id,
    source.snapshot_date,
    source.view_count,
    source.like_count,
    source.comment_count,
    source.favorite_count,
    source.collected_at,
    source.run_id
);