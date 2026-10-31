-- 1. Tạo bảng Bronze nếu chưa tồn tại
CREATE TABLE IF NOT EXISTS
`youtube-pipeline-512201.bronze_youtube.bronze_channels`
(
    channel_id STRING,
    channel_title STRING,
    description STRING,
    custom_url STRING,
    country STRING,
    published_at TIMESTAMP,
    uploads_playlist_id STRING,
    view_count INT64,
    subscriber_count INT64,
    video_count INT64,
    collected_at TIMESTAMP,
    run_id STRING
);

-- 2. Thêm run_id nếu bảng cũ chưa có
ALTER TABLE
`youtube-pipeline-512201.bronze_youtube.bronze_channels`
ADD COLUMN IF NOT EXISTS run_id STRING;

-- 3. Bóc tách JSON và APPEND vào Bronze
INSERT INTO
`youtube-pipeline-512201.bronze_youtube.bronze_channels`
(
    channel_id,
    channel_title,
    description,
    custom_url,
    country,
    published_at,
    uploads_playlist_id,
    view_count,
    subscriber_count,
    video_count,
    collected_at,
    run_id
)

SELECT
    JSON_VALUE(item, '$.id') AS channel_id,

    JSON_VALUE(item, '$.snippet.title') AS channel_title,

    JSON_VALUE(item, '$.snippet.description') AS description,

    JSON_VALUE(item, '$.snippet.customUrl') AS custom_url,

    JSON_VALUE(item, '$.snippet.country') AS country,

    SAFE_CAST(
        JSON_VALUE(item, '$.snippet.publishedAt')
        AS TIMESTAMP
    ) AS published_at,

    JSON_VALUE(
        item,
        '$.contentDetails.relatedPlaylists.uploads'
    ) AS uploads_playlist_id,

    SAFE_CAST(
        JSON_VALUE(item, '$.statistics.viewCount')
        AS INT64
    ) AS view_count,

    SAFE_CAST(
        JSON_VALUE(item, '$.statistics.subscriberCount')
        AS INT64
    ) AS subscriber_count,

    SAFE_CAST(
        JSON_VALUE(item, '$.statistics.videoCount')
        AS INT64
    ) AS video_count,

    SAFE_CAST(
        JSON_VALUE(r.payload, '$.collected_at')
        AS TIMESTAMP
    ) AS collected_at,

    JSON_VALUE(r.payload, '$.run_id') AS run_id

FROM `youtube-pipeline-512201.raw_youtube.raw_channels` AS r

CROSS JOIN UNNEST(
    JSON_QUERY_ARRAY(r.payload, '$.data.items')
) AS item

WHERE JSON_VALUE(item, '$.id') IS NOT NULL

-- Tránh INSERT lại bản ghi đã xử lý
AND NOT EXISTS (
    SELECT 1
    FROM `youtube-pipeline-512201.bronze_youtube.bronze_channels` AS b
    WHERE b.run_id = JSON_VALUE(r.payload, '$.run_id')
      AND b.channel_id = JSON_VALUE(item, '$.id')
);