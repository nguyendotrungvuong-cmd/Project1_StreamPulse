SELECT distinct
    video_id,
    
    
FROM `youtube-pipeline-512201.bronze_youtube.bronze_uploads`
WHERE
    LOWER(video_title) LIKE '%tinh hà say hi%'
    OR LOWER(video_title) LIKE '%thsh%'
    OR LOWER(video_title) LIKE '%tinh ha say hi%'
