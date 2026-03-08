-- ============================================================
-- SCRIPT DE CRÉATION DE LA BASE DE DONNÉES
-- Exécuter dans pgAdmin ou psql
-- ============================================================

-- 1. Créer la base de données (à exécuter en tant que postgres)
-- CREATE DATABASE dashboard_db;

-- Se connecter à dashboard_db avant d'exécuter la suite

-- ============================================================
-- TABLE PERSONS : données fictives des utilisateurs
-- ============================================================
CREATE TABLE IF NOT EXISTS persons (
    id                SERIAL PRIMARY KEY,
    nom               VARCHAR(100) NOT NULL,
    prenom            VARCHAR(100) NOT NULL,
    email             VARCHAR(200),
    telephone         VARCHAR(50),
    adresse           TEXT,
    ville             VARCHAR(100),
    code_postal       VARCHAR(10),
    region            VARCHAR(100),
    latitude          DECIMAL(9, 6),
    longitude         DECIMAL(9, 6),
    age               INTEGER,
    probleme          TEXT,
    solution          TEXT,
    statut            VARCHAR(50) DEFAULT 'Ouvert',
    est_doublon       BOOLEAN DEFAULT FALSE,
    date_creation     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE METEO : données météo par région
-- ============================================================
CREATE TABLE IF NOT EXISTS meteo (
    id                    SERIAL PRIMARY KEY,
    region                VARCHAR(100) NOT NULL,
    ville_reference       VARCHAR(100),
    latitude              DECIMAL(9, 6),
    longitude             DECIMAL(9, 6),
    temperature           DECIMAL(5, 2),
    temperature_ressentie DECIMAL(5, 2),
    humidite              INTEGER,
    vitesse_vent          DECIMAL(6, 2),
    direction_vent        INTEGER,
    precipitation         DECIMAL(6, 2),
    pression              DECIMAL(8, 2),
    couverture_nuageuse   INTEGER,
    code_meteo            INTEGER,
    description_meteo     VARCHAR(100),
    timestamp_collecte    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- VUES POUR POWER BI
-- ============================================================

-- Vue : dernière météo par région (Power BI rafraîchit cette vue)
CREATE OR REPLACE VIEW v_meteo_derniere AS
SELECT DISTINCT ON (region)
    id,
    region,
    ville_reference,
    latitude,
    longitude,
    temperature,
    temperature_ressentie,
    humidite,
    vitesse_vent,
    precipitation,
    description_meteo,
    timestamp_collecte
FROM meteo
ORDER BY region, timestamp_collecte DESC;

-- Vue : nombre de problèmes par région
CREATE OR REPLACE VIEW v_problemes_par_region AS
SELECT
    region,
    COUNT(*)                                        AS total_signalements,
    COUNT(*) FILTER (WHERE statut = 'Ouvert')       AS ouverts,
    COUNT(*) FILTER (WHERE statut = 'En cours')     AS en_cours,
    COUNT(*) FILTER (WHERE statut = 'Résolu')       AS resolus,
    COUNT(*) FILTER (WHERE statut = 'Fermé')        AS fermes,
    COUNT(*) FILTER (WHERE est_doublon = TRUE)      AS doublons,
    ROUND(AVG(age))                                 AS age_moyen,
    AVG(latitude)                                   AS lat_centre,
    AVG(longitude)                                  AS lon_centre
FROM persons
GROUP BY region;

-- Vue : dashboard principal combiné (météo + problèmes)
CREATE OR REPLACE VIEW v_dashboard_principal AS
SELECT
    p.region,
    p.total_signalements,
    p.ouverts,
    p.en_cours,
    p.resolus,
    p.fermes,
    p.doublons,
    p.age_moyen,
    p.lat_centre,
    p.lon_centre,
    m.temperature,
    m.temperature_ressentie,
    m.humidite,
    m.vitesse_vent,
    m.precipitation,
    m.description_meteo,
    m.timestamp_collecte AS derniere_maj_meteo
FROM v_problemes_par_region p
LEFT JOIN v_meteo_derniere m ON p.region = m.region;

-- Vue : répartition des types de problèmes
CREATE OR REPLACE VIEW v_types_problemes AS
SELECT
    probleme,
    COUNT(*)                                    AS nombre,
    COUNT(*) FILTER (WHERE statut = 'Résolu')   AS resolus,
    ROUND(
        COUNT(*) FILTER (WHERE statut = 'Résolu') * 100.0 / COUNT(*), 1
    )                                           AS taux_resolution_pct
FROM persons
GROUP BY probleme
ORDER BY nombre DESC;

-- Vue : évolution temporelle des signalements
CREATE OR REPLACE VIEW v_evolution_signalements AS
SELECT
    DATE_TRUNC('day', date_creation)    AS jour,
    region,
    COUNT(*)                            AS signalements_jour,
    COUNT(*) FILTER (WHERE est_doublon) AS doublons_jour
FROM persons
GROUP BY DATE_TRUNC('day', date_creation), region
ORDER BY jour DESC;

-- Vue : évolution température dans le temps
CREATE OR REPLACE VIEW v_evolution_meteo AS
SELECT
    DATE_TRUNC('hour', timestamp_collecte)  AS heure,
    region,
    AVG(temperature)                        AS temp_moyenne,
    AVG(humidite)                           AS humidite_moyenne,
    AVG(precipitation)                      AS precip_moyenne
FROM meteo
GROUP BY DATE_TRUNC('hour', timestamp_collecte), region
ORDER BY heure DESC;

-- ============================================================
-- INDEX pour performances
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_persons_region      ON persons(region);
CREATE INDEX IF NOT EXISTS idx_persons_statut      ON persons(statut);
CREATE INDEX IF NOT EXISTS idx_persons_date        ON persons(date_creation);
CREATE INDEX IF NOT EXISTS idx_meteo_region        ON meteo(region);
CREATE INDEX IF NOT EXISTS idx_meteo_timestamp     ON meteo(timestamp_collecte);

-- ============================================================
-- Vérification
-- ============================================================
SELECT 'Tables créées avec succès !' AS message;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
