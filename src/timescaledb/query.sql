SELECT 
    time_bucket_gapfill('5 minutes'::interval, metric.time, :time_bucket_gapfill_1, :time_bucket_gapfill_2) AS bucket, 
    locf(avg(metric.temp)) AS avg 
FROM metric 
    GROUP BY 
        time_bucket_gapfill('5 minutes'::interval, metric.time, :time_bucket_gapfill_1, :time_bucket_gapfill_2) 
        ORDER BY time_bucket_gapfill('5 minutes'::interval, metric.time, :time_bucket_gapfill_1, :time_bucket_gapfill_2) ASC