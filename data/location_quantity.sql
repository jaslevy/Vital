SELECT 
    l.location_id location_id,
    l.hall hall, 
    l.door_number door, 
    l.floor_number floor,
    l.longitude longitude, 
    l.latitude latiutude, 
    q.tampon_count tampon_count,
    q.pad_count pad_count,
    q.condom_count condom_count,
    q.time_updated::DATE last_time_updated,
    q.time_restocked::DATE last_time_restocked
FROM locations l
INNER JOIN quantities q
    ON l.location_id = q.location_id