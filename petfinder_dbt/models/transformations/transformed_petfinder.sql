{{ config(
    materialized='table',
    partition_by={'field': 'published_at', 'data_type': 'TIMESTAMP'},
    cluster_by=['species', 'age_group', 'state']
) }}

WITH cleaned_data AS (
    SELECT
        id,
        name,
        species,
        age,
        gender,
        size,
        primary_breed,
        primary_color,
        CAST(spayed_neutered AS BOOL) AS spayed_neutered,
        CAST(house_trained AS BOOL) AS house_trained,
        CAST(declawed AS BOOL) AS declawed,
        CAST(special_needs AS BOOL) AS special_needs,
        CAST(shots_current AS BOOL) AS shots_current,
        CAST(good_with_children AS BOOL) AS good_with_children,
        CAST(good_with_dogs AS BOOL) AS good_with_dogs,
        CAST(good_with_cats AS BOOL) AS good_with_cats,
        tags,
        location,
        SPLIT(location, ', ')[SAFE_OFFSET(0)] AS city,
        SPLIT(location, ', ')[SAFE_OFFSET(1)] AS state,
        postcode,
        published_at,
        organization_id,
        email,
        ARRAY_TO_STRING(tags, ', ') AS tags_string,
        CASE
            WHEN age = 'Baby' THEN '0-1 years'
            WHEN age = 'Young' THEN '1-3 years'
            WHEN age = 'Adult' THEN '3-7 years'
            WHEN age = 'Senior' THEN '7+ years'
            ELSE 'Unknown'
        END AS age_group
    FROM {{ ref('stg_petfinder') }}
)

SELECT * FROM cleaned_data
