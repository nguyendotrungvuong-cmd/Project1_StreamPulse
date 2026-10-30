SELECT
    channel_id,
    uploads_playlist_id
FROM `youtube-pipeline-512201.bronze_youtube.bronze_channels`
WHERE uploads_playlist_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY channel_id
    ORDER BY collected_at DESC
) = 1;