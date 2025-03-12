WITH raw AS (
    SELECT
        id,
        name,
        species,
        age,
        gender,
        size,
        coat,
        status,
        primary_breed,
        secondary_breed,
        mixed_breed,
        location,
        TIMESTAMP(published_at) AS published_at
    FROM `petfinderapi.petfinder_data.raw_petfinder`
)

SELECT * FROM raw
WHERE status = 'adoptable'  -- Only include adoptable pets
