-- 1. Tạo bảng nếu chưa tồn tại
CREATE TABLE IF NOT EXISTS
`youtube-pipeline-512201.bronze_youtube.bronze_videos_statistics`
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

    view_count INT64,
    like_count INT64,
    comment_count INT64,
    favorite_count INT64,

    collected_at TIMESTAMP,
    run_id STRING
);



-- 3. Bóc JSON và APPEND
INSERT INTO
`youtube-pipeline-512201.bronze_youtube.bronze_videos_statistics`
(
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

    view_count,
    like_count,
    comment_count,
    favorite_count,

    collected_at,
    run_id
)

SELECT
    JSON_VALUE(item, '$.id') AS video_id,

    JSON_VALUE(item, '$.snippet.channelId') AS channel_id,

    JSON_VALUE(item, '$.snippet.channelTitle') AS channel_title,

    JSON_VALUE(item, '$.snippet.title') AS video_title,

    JSON_VALUE(item, '$.snippet.description') AS description,

    SAFE_CAST(
        JSON_VALUE(item, '$.snippet.publishedAt')
        AS TIMESTAMP
    ) AS published_at,

    JSON_VALUE(item, '$.snippet.categoryId') AS category_id,

    JSON_VALUE(item, '$.snippet.defaultLanguage') AS default_language,

    JSON_VALUE(item, '$.snippet.thumbnails.high.url') AS thumbnail_url,

    JSON_VALUE_ARRAY(item, '$.snippet.tags') AS tags,

    SAFE_CAST(
        JSON_VALUE(item, '$.statistics.viewCount')
        AS INT64
    ) AS view_count,

    SAFE_CAST(
        JSON_VALUE(item, '$.statistics.likeCount')
        AS INT64
    ) AS like_count,

    SAFE_CAST(
        JSON_VALUE(item, '$.statistics.commentCount')
        AS INT64
    ) AS comment_count,

    SAFE_CAST(
        JSON_VALUE(item, '$.statistics.favoriteCount')
        AS INT64
    ) AS favorite_count,

    SAFE_CAST(
        JSON_VALUE(r.payload, '$.collected_at')
        AS TIMESTAMP
    ) AS collected_at,

    JSON_VALUE(r.payload, '$.run_id') AS run_id

FROM `youtube-pipeline-512201.raw_youtube.raw_video_statistics` AS r

CROSS JOIN UNNEST(
    JSON_QUERY_ARRAY(r.payload, '$.data')
) AS response

CROSS JOIN UNNEST(
    JSON_QUERY_ARRAY(response, '$.items')
) AS item

WHERE JSON_VALUE(item, '$.id') IS NOT NULL;