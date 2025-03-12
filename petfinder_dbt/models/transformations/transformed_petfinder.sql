WITH cleaned_data AS (
    SELECT
        id,
        name,
        species,
        age,
        gender,
        size,
        primary_breed,
        secondary_breed,
        mixed_breed,
        location,
        published_at,
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
