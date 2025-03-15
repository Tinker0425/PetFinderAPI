WITH raw AS (
    SELECT
        id,
        name,
        species,
        age,
        gender,
        size,
        status,
        primary_breed,
        primary_color,
        spayed_neutered,
        house_trained,
        declawed,
        special_needs,
        shots_current,
        good_with_children,
        good_with_dogs,
        good_with_cats,
        tags,
        location,
        postcode,
        TIMESTAMP(published_at) AS published_at,
        organization_id,
        email
    FROM `petfinderapi.petfinder_data.raw_petfinder`
)

SELECT * FROM raw
WHERE status = 'adoptable'  -- Only include adoptable pets
