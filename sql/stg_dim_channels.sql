CREATE OR REPLACE TABLE
`youtube-pipeline-512201.staging_youtube.stg_dim_channels`
AS

SELECT
    channel_id,
    channel_title,
    description,
    custom_url,
    country,
    published_at,
    uploads_playlist_id,
    collected_at,
    run_id

FROM `youtube-pipeline-512201.bronze_youtube.bronze_channels`

WHERE channel_id IS NOT NULL
 

QUALIFY ROW_NUMBER() OVER (
    PARTITION BY channel_id
    ORDER BY collected_at DESC
) = 1;