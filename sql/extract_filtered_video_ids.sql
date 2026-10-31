SELECT DISTINCT
    video_id
FROM `youtube-pipeline-512201.bronze_youtube.bronze_uploads`
WHERE
    LOWER(video_title) LIKE CONCAT('%', LOWER(@show), '%')
    OR LOWER(description) LIKE CONCAT('%#', LOWER(@show), '%');