CREATE TABLE IF NOT EXISTS
`youtube-pipeline-512201.silver_youtube.fact_channel_stats`
(
    channel_id STRING,
    snapshot_date DATE,
    subscriber_count INT64,
    view_count INT64,
    video_count INT64,
    collected_at TIMESTAMP,
    run_id STRING
)
PARTITION BY snapshot_date
CLUSTER BY channel_id;

MERGE `youtube-pipeline-512201.silver_youtube.fact_channel_stats` AS target
USING `youtube-pipeline-512201.staging_youtube.stg_fact_channel_stats` AS source

ON target.channel_id = source.channel_id
AND target.snapshot_date = source.snapshot_date

WHEN MATCHED
    AND (
        target.collected_at IS NULL
        OR source.collected_at > target.collected_at
    )
THEN UPDATE SET
    subscriber_count = source.subscriber_count,
    view_count = source.view_count,
    video_count = source.video_count,
    collected_at = source.collected_at,
    run_id = source.run_id

WHEN NOT MATCHED THEN
INSERT (
    channel_id,
    snapshot_date,
    subscriber_count,
    view_count,
    video_count,
    collected_at,
    run_id
)
VALUES (
    source.channel_id,
    source.snapshot_date,
    source.subscriber_count,
    source.view_count,
    source.video_count,
    source.collected_at,
    source.run_id
);