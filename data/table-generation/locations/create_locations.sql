-- Specify where each of the locations are
CREATE TABLE IF NOT EXISTS locations (
    location_id     SERIAL PRIMARY KEY  NOT NULL,
    hall            VARCHAR(50)         NOT NULL,
    door_number     int                 NOT NULL,
    floor_number    int                 NOT NULL,
    latitude        decimal             NOT NULL,
    longitude       decimal             NOT NULL,
    notes           varchar(256)
);