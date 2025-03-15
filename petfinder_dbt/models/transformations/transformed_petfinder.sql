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
        location,
        SPLIT(location, ', ')[SAFE_OFFSET(0)] AS city,
        SPLIT(location, ', ')[SAFE_OFFSET(1)] AS state,
        postcode,
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
