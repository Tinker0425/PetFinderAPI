SELECT
    id,
    name,
    species,
    age,
    gender,
    size,
    status,
    location
FROM `'raw_petfinder'`
WHERE status = 'adoptable'
