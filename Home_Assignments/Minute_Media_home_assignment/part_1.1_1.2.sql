-- 1. Using SQL: Identify any data quality issues and suggest potential solutions for them.

SELECT max(time_utc), min(time_utc)
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`; --data goes from 25.9.24 to 9.10.24

-- how many distinct and overall sessions do we have? 112,920,726 and 1,468,962,942 --> this means that some sessionid are duplicated
select count(distinct sessionid) distinct_sessions, count(sessionid) session_count
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`;

-- how many null or empty sessionid  do we have?
select sessionid, count(*)
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
where sessionid is null or sessionid like ''
group by 1; -- 20,971,332 (1% of 1,468,962,942) null and 68,180 (0.005% of 1,468,962,942)empty --> these can be dropped as it's a negligible percentage


-- do we have multiple devices per session?
select count(distinct sessionid)
from
(select sessionid, count(distinct device) as num_devices_per_session
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
having count(distinct device) > 1
); -- we have 71,186 (0.06% of 112,920,726) sessionid that have more than 1 device and 99% that have 1 device

# what are the sessionid that have more than one device?

select *
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
where sessionid in (select distinct sessionid
from
(select sessionid, count(distinct device) as num_devices_per_session
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
having count(distinct device) > 1
));


-- let's see what are the most common profiles of sessions that have multiple devices
select EXTRACT(DAYOFWEEK FROM time_utc) AS day_of_week, -- Sunday = 1, Monday = 2, ..., Saturday = 7
  CASE
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 0 AND 5 THEN 'night'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 6 AND 11 THEN 'morning'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 12 AND 17 THEN 'afternoon'
    ELSE 'evening'
  END AS time_range,
browser, platform, count(distinct sessionid) num_sessions
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
where sessionid in (select distinct sessionid
from
(select sessionid, count(distinct device) as num_devices_per_session
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
having count(distinct device) > 1
))
and browser is not null and platform is not null
group by 1,2,3,4
order by 5 desc; -- sessions done on wednesday morning from android chrome are the most frequent sessions to have another device


-- what's the device with the higher total number of sessions?

select device, count(distinct sessionid) num_sessions
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc; --mobile desktop and tablet are the devices with highest number of sessions

-- what's the browser with the higher total number of sessions?
select browser, count(distinct sessionid) num_sessions
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc; --mobile chrome and mobile safari are the most common browsers

-- what's the platform with the higher total number of sessions?
select platform, count(distinct sessionid) num_sessions
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc; -- android and iOS are the most common platforms

-- what's the platformVersion with the higher total number of sessions?

select platformVersion, count(distinct sessionid) num_sessions
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc; -- 10 and 17.6.1 versions are the most common

-- what's the event with the higher total number of sessions?

select event, count(distinct sessionid) num_sessions
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc; --pageView and session are the most common types of events

-- -- can we spot these sessions: sessions that do not have session and pageView events reported (sessions from our clients that do not belong to our owned and operated sites)
--
-- WITH filtered_events AS (
--   SELECT
--     sessionid,
--     ARRAY_AGG(DISTINCT event) AS event_types
--   FROM
--     `mmtestout.gioiablayer.dsEmployeeTestFinal`
--   GROUP BY
--     sessionid
-- ),
-- invalid_sessions AS (
--   SELECT
--     sessionid
--   FROM
--     filtered_events
--   WHERE
--     -- Ensure no 'session' or 'pageView' events are present
--     NOT EXISTS (
--       SELECT 1
--       FROM UNNEST(event_types) AS event
--       WHERE event IN ('session', 'pageView')
--     )
--     AND
--     -- Ensure only the specified events are present
--     ARRAY_LENGTH(
--       ARRAY(
--         SELECT event
--         FROM UNNEST(event_types) AS event
--         WHERE event NOT IN ('videoPlayerEmbed', 'displayImpression', 'videoImpression')
--       )
--     ) = 0
-- )
-- SELECT count(distinct sessionid)
-- FROM
--   invalid_sessions; --2,390,122 sessions (2% of 112,920,726) are missing session or pageview events because these are sessions that do not belong to MM sites.


-- what's the profile (day of week, time range, device, browser, platform, version, event) with the highest total number of sessions?


select EXTRACT(DAYOFWEEK FROM time_utc) AS day_of_week, -- Sunday = 1, Monday = 2, ..., Saturday = 7
  CASE
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 0 AND 5 THEN 'night'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 6 AND 11 THEN 'morning'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 12 AND 17 THEN 'afternoon'
    ELSE 'evening'
  END AS time_range, device, browser, platform, platformVersion, event, count(distinct sessionid) num_sessions
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
where device is not null and browser is not null and platform is not null and platformVersion is not null
group by 1,2,3,4,5,6,7
order by 8 desc;
-- the most common profile is: pageViews done on wednseday night from a mobile android device, with chrome browser v10.

-- do we have multiple browser per session?

select sessionid, count(distinct browser) as num_browsers
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
having count(distinct browser) > 1
order by 2 desc; -- 69,707 (0.06% of sessions) have more than 1 browser


-- do we have multiple platform per session?

select sessionid, count(distinct platform) as num_platforms
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
having count(distinct platform) > 1
order by 2 desc; -- 20,920 (0.02% of sessions) have more than 1 platform

-- do we have multiple platformVersion per session?

select sessionid, count(distinct platformVersion) as num_platformV
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
having count(distinct platformVersion) > 1
order by 2 desc; -- 32,183 (0.03% of sessions) have more than 1 platformVersion

-- do we have multiple event per session?

select sessionid, count(distinct event) as num_events
from `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
having count(distinct event) > 1
order by 2 desc; -- 110,529,806 (98% of sessionid) have more than 1 events.


-- missing values in device column
SELECT device, count(*)/(select sum(row_count)
from
(SELECT device, count(*) as row_count
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc
))
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc; -- 8% missing values in device

-- missing values in browser column

SELECT browser, count(*)/(select sum(row_count)
from
(SELECT browser, count(*) as row_count
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc
))
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc; -- 10% of missing values in browser

-- missing values in platform column

SELECT platform, count(*)/(select sum(row_count)
from
(SELECT platform, count(*) as row_count
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc
))
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc; -- 10% of missing values in platform

-- missing values in platformVersion column

SELECT platformVersion, count(*)/(select sum(row_count)
from
(SELECT platformVersion, count(*) as row_count
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc
))
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc; -- 10% of missing values in platform

-- missing values in events column: NO missing values

SELECT event, count(*)/(select sum(row_count)
from
(SELECT event, count(*) as row_count
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc
))
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
group by 1
order by 2 desc;

-- descriptive statistics of revenue: missing values, mean, median, min, max

select count(*), count(distinct sessionid)
FROM `mmtestout.gioiablayer.dsEmployeeTestFinal`
where revenue is null; -- 112,876,495 (99% of sessions, the revenue is null)


SELECT
  PERCENTILE_CONT(revenue, 0.25) OVER() AS revenue_25th_percentile,
  PERCENTILE_CONT(revenue, 0.50) OVER() AS revenue_50th_percentile,
  PERCENTILE_CONT(revenue, 0.75) OVER() AS revenue_75th_percentile
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal` --25 percentile is 0.00149. 50 percentile is 0.00338, 75 percentile is 0.0059
WHERE
  revenue IS NOT NULL;

SELECT
  AVG(revenue) AS avg_revenue,
  COUNT(DISTINCT sessionid) AS unique_sessions,
  COUNT(*) AS total_rows,
  MIN(revenue) AS min_revenue,
  MAX(revenue) AS max_revenue,
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL; -- avg: 0.004, unique sessions: 88,883,871. min revenue:0, max revenue: 0.87

-- in which time period (time range) do we have the highest average revenue?

select
  CASE
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 0 AND 5 THEN 'night'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 6 AND 11 THEN 'morning'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 12 AND 17 THEN 'afternoon'
    ELSE 'evening'
  END AS time_range,
  avg(revenue) avg_revenue,
  count(distinct sessionid) as num_sessions
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL
group by 1
order by 2 desc; -- morning is the time range with avg highest revenue per session

-- in which time period (day of week) do we have the highest average revenue?

select
  EXTRACT(DAYOFWEEK FROM time_utc) AS day_of_week, --sunday=1
  avg(revenue) avg_revenue,
  count(distinct sessionid) as num_sessions
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL
group by 1
order by 2 desc; --friday is the day with highest avg revenue

-- for which device do we have the highest average revenue?

SELECT
  CASE
    WHEN LOWER(device) IN ('phone', 'mobile') THEN 'mobile'
    ELSE LOWER(device)
  END AS device_category, -- Merges phone and mobile into 'mobile'
  AVG(revenue) AS avg_revenue,
  COUNT(DISTINCT sessionid) AS num_sessions
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL
GROUP BY
  device_category
ORDER BY
  avg_revenue DESC; --highest revenue is from crawlers. for significant inference I will drop this category


-- for which browser do we have the highest average revenue?

select count(distinct sessionid)
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL; -- from power analysis, for a 98% confidence level and 1% error margin i should have at least 15,000 sessionid for statistically significant inference (because the finite population is of 88M sessions).

select
  browser,
  avg(revenue) avg_revenue,
  count(distinct sessionid) as num_sessions
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL
group by 1
having count(distinct sessionid) > 15000
order by 2 desc; --duckduck go is the most lucrative browsers (statistically significant)

-- for which platform do we have the highest average revenue?
select
  platform,
  avg(revenue) avg_revenue,
  count(distinct sessionid) as num_sessions
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL
group by 1
having count(distinct sessionid) > 15000
order by 2 desc; -- android and linus are the platforms with statistically significant higher revenue


-- for which platformVersion do we have the highest average revenue?

select
  platformVersion,
  avg(revenue) avg_revenue,
  count(distinct sessionid) as num_sessions
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL
group by 1
having count(distinct sessionid) > 15000
order by 2 desc; --version 10 of the platform has the highest avg revenue (significant)

-- for which event do we have the highest average revenue?

select
  event,
  avg(revenue) avg_revenue,
  count(distinct sessionid) as num_sessions
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL
group by 1
having count(distinct sessionid) > 15000
order by 2 desc; -- video impression and display impression are the events with highest avg revenue

-- for which profile/segment do we have the highest average revenue?

select
CASE
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 0 AND 5 THEN 'night'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 6 AND 11 THEN 'morning'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 12 AND 17 THEN 'afternoon'
    ELSE 'evening'
  END AS time_range,
  EXTRACT(DAYOFWEEK FROM time_utc) AS day_of_week,
  CASE
    WHEN LOWER(device) IN ('phone', 'mobile') THEN 'mobile'
    ELSE LOWER(device)
  END AS device_category,
  browser,
  platform,
  platformVersion,
  event,
  avg(revenue) avg_revenue,
  count(distinct sessionid) as num_sessions
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
WHERE
  revenue IS NOT NULL and browser is not null and platform is not null and platformVersion is not null
group by 1,2,3,4,5,6,7
having count(distinct sessionid) > 15000
order by 8 desc;
-- videoImpressions done during sunday morning from chrome mobile (v10) on an android device have the highest average revenue (statistically significant)

-- create a CSV with aggregated data - can i answer some of the above questions with aggregated data?

SELECT
  EXTRACT(DAYOFWEEK FROM time_utc) AS day_of_week, -- Sunday = 1, Monday = 2, ..., Saturday = 7
  CASE
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 0 AND 5 THEN 'night'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 6 AND 11 THEN 'morning'
    WHEN EXTRACT(HOUR FROM time_utc) BETWEEN 12 AND 17 THEN 'afternoon'
    ELSE 'evening'
  END AS time_range,
  CASE
    WHEN LOWER(device) IN ('phone', 'mobile') THEN 'mobile'
    ELSE LOWER(device)
  END AS device,
  browser,
  platform,
  platformVersion,
  event,
  count(distinct sessionid) num_distinct_sessions,
  sum(revenue) total_revenue
FROM
  `mmtestout.gioiablayer.dsEmployeeTestFinal`
where
device is not null
and device not in ('crawler')
and browser is not null
and platform is not null
and platformVersion is not null
and revenue is not null
and sessionid is not null
and sessionid not in ('')
and sessionid not in (WITH filtered_events AS (
  SELECT
    sessionid,
    ARRAY_AGG(DISTINCT event) AS event_types
  FROM
    `mmtestout.gioiablayer.dsEmployeeTestFinal`
  GROUP BY
    sessionid
),
invalid_sessions AS (
  SELECT
    sessionid
  FROM
    filtered_events
  WHERE
    -- Ensure no 'session' or 'pageView' events are present
    NOT EXISTS (
      SELECT 1
      FROM UNNEST(event_types) AS event
      WHERE event IN ('session', 'pageView')
    )
    AND
    -- Ensure only the specified events are present
    ARRAY_LENGTH(
      ARRAY(
        SELECT event
        FROM UNNEST(event_types) AS event
        WHERE event NOT IN ('videoPlayerEmbed', 'displayImpression', 'videoImpression')
      )
    ) = 0
)
SELECT distinct sessionid
FROM
  invalid_sessions)
group by 1,2,3,4,5,6,7


