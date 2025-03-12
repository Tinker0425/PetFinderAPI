SELECT
    id,
    name,
    species,
    age,
    gender,
    size,
    status,
    location
FROM `{{ var('raw_petfinder_table') }}`
WHERE status = 'adoptable'
