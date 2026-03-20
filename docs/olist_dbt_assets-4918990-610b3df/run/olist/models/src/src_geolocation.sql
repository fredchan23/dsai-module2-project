
  create or replace   view OLIST.DEV.src_geolocation
  
  
  
  
  as (
    select
    cast("geolocation_zip_code_prefix" as varchar(5)) as geolocation_zip_code_prefix,
    cast("geolocation_lat" as number(10, 6)) as geolocation_lat,
    cast("geolocation_lng" as number(10, 6)) as geolocation_lng,
    trim("geolocation_city") as geolocation_city,
    trim("geolocation_state") as geolocation_state
from OLIST.RAW.raw_geolocation
  );

