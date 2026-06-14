CREATE TABLE ods.fct_weather
(
    time varchar
    , temperature_2m_c varchar
    , relative_humidity_2m varchar
    , dew_point_2m_c varchar
    , latitude varchar
    , longitude varchar
    , elevation varchar
    , timezone varchar
);

CREATE TABLE dm.fct_count_day_weather AS 
SELECT time::date AS date, count(*)
FROM ods.fct_weather
GROUP BY 1 ;

CREATE TABLE dm.fct_avg_day_weather AS
SELECT time::date AS date, avg(temperature_2m_c::float)
FROM ods.fct_weather
GROUP BY 1 ;

