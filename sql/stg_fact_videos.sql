CREATE OR REPLACE TABLE
`youtube-pipeline-512201.staging_youtube.stg_fact_video_stats`
AS

SELECT
    video_id,
    channel_id,

    DATE(
        collected_at,
        'Asia/Ho_Chi_Minh'
    ) AS snapshot_date,

    view_count,
    like_count,
    comment_count,
    favorite_count,

    collected_at,
    run_id

FROM `youtube-pipeline-512201.bronze_youtube.bronze_videos_statistics`

WHERE video_id IS NOT NULL
  AND collected_at IS NOT NULL

QUALIFY ROW_NUMBER() OVER (
    PARTITION BY
        video_id,
        DATE(collected_at, 'Asia/Ho_Chi_Minh')

    ORDER BY collected_at DESC, run_id DESC
) = 1;