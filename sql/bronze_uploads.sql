-- 1. Tạo bảng Bronze nếu chưa tồn tại
CREATE TABLE IF NOT EXISTS
`youtube-pipeline-512201.bronze_youtube.bronze_uploads`
(
    video_id STRING,
    channel_id STRING,
    channel_title STRING,
    video_title STRING,
    description STRING,
    published_at TIMESTAMP,
    playlist_id STRING,
    playlist_item_id STRING,
    position INT64,
    run_id STRING,
    collected_at TIMESTAMP
);
-- 3. Bóc JSON và APPEND vào Bronze
INSERT INTO
`youtube-pipeline-512201.bronze_youtube.bronze_uploads`
(
    video_id,
    channel_id,
    channel_title,
    video_title,
    description,
    published_at,
    playlist_id,
    playlist_item_id,
    position,
    run_id,
    collected_at
)

SELECT
    JSON_VALUE(item, '$.contentDetails.videoId') AS video_id,

    JSON_VALUE(item, '$.snippet.channelId') AS channel_id,

    JSON_VALUE(item, '$.snippet.channelTitle') AS channel_title,

    JSON_VALUE(item, '$.snippet.title') AS video_title,

    JSON_VALUE(item, '$.snippet.description') AS description,

    SAFE_CAST(
        JSON_VALUE(item, '$.contentDetails.videoPublishedAt')
        AS TIMESTAMP
    ) AS published_at,

    JSON_VALUE(item, '$.snippet.playlistId') AS playlist_id,

    JSON_VALUE(item, '$.id') AS playlist_item_id,

    SAFE_CAST(
        JSON_VALUE(item, '$.snippet.position')
        AS INT64
    ) AS position,

    JSON_VALUE(r.payload, '$.run_id') AS run_id,

    SAFE_CAST(
        JSON_VALUE(r.payload, '$.collected_at')
        AS TIMESTAMP
    ) AS collected_at

FROM `youtube-pipeline-512201.raw_youtube.raw_uploads` AS r

CROSS JOIN UNNEST(
    JSON_QUERY_ARRAY(r.payload, '$.data')
) AS response

CROSS JOIN UNNEST(
    JSON_QUERY_ARRAY(response, '$.items')
) AS item

WHERE JSON_VALUE(item, '$.contentDetails.videoId') IS NOT NULL;