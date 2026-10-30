CREATE OR REPLACE TABLE
`youtube-pipeline-512201.staging_youtube.stg_fact_channel_stats`
AS

SELECT
    channel_id,

    DATE(
        collected_at,
        'Asia/Ho_Chi_Minh'
    ) AS snapshot_date,

    subscriber_count,
    view_count,
    video_count,

    collected_at,
    run_id

FROM `youtube-pipeline-512201.bronze_youtube.bronze_channels`

WHERE channel_id IS NOT NULL
  AND collected_at IS NOT NULL
  

QUALIFY ROW_NUMBER() OVER (
    PARTITION BY
        channel_id,
        DATE(collected_at, 'Asia/Ho_Chi_Minh')

    ORDER BY collected_at DESC
) = 1;