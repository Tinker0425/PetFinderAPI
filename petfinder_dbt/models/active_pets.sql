SELECT
    id,
    name,
    species,
    age,
    gender,
    size,
    status,
    location
FROM `petfinderapi.petfinder_data.raw_petfinder`
WHERE status = 'adoptable'
