
    SELECT
        i.risk,
        COALESCE(r.description, 'Unmapped') AS description,
        COUNT(*) AS total_inspections,
        SUM(
            CASE
                WHEN i.results = 'Fail' THEN 1
                ELSE 0
            END
        ) AS failed_inspections
    FROM inspections AS i
    LEFT JOIN risk_lookup AS r
        ON i.risk = r.risk
    GROUP BY i.risk, r.description
    ORDER BY total_inspections DESC;
    