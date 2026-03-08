"""
Script de récupération météo en temps réel
Utilise l'API Open-Meteo (gratuite, sans clé API requise)
Récupère la météo pour chaque région française
"""

import requests
import psycopg2
from datetime import datetime
import logging
import time
import os
import sys


# Ajouter le dossier parent au path pour trouver config

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Coordonnées des capitales régionales
REGIONS_METEO = {
    "Île-de-France":               {"lat": 48.8566, "lon": 2.3522,  "ville": "Paris"},
    "Auvergne-Rhône-Alpes":        {"lat": 45.7640, "lon": 4.8357,  "ville": "Lyon"},
    "Provence-Alpes-Côte d'Azur":  {"lat": 43.2965, "lon": 5.3698,  "ville": "Marseille"},
    "Nouvelle-Aquitaine":          {"lat": 44.8378, "lon": -0.5792, "ville": "Bordeaux"},
    "Occitanie":                   {"lat": 43.6047, "lon": 1.4442,  "ville": "Toulouse"},
    "Hauts-de-France":             {"lat": 50.6292, "lon": 3.0573,  "ville": "Lille"},
    "Grand Est":                   {"lat": 48.5734, "lon": 7.7521,  "ville": "Strasbourg"},
    "Normandie":                   {"lat": 49.4432, "lon": 1.0993,  "ville": "Rouen"},
    "Bretagne":                    {"lat": 48.1173, "lon": -1.6778, "ville": "Rennes"},
    "Pays de la Loire":            {"lat": 47.2184, "lon": -1.5536, "ville": "Nantes"},
    "Centre-Val de Loire":         {"lat": 47.9029, "lon": 1.9093,  "ville": "Orléans"},
    "Bourgogne-Franche-Comté":     {"lat": 47.3220, "lon": 5.0415,  "ville": "Dijon"},
}

# Codes météo WMO → description
WMO_CODES = {
    0: "Ciel dégagé", 1: "Principalement dégagé", 2: "Partiellement nuageux",
    3: "Couvert", 45: "Brouillard", 48: "Brouillard givrant",
    51: "Bruine légère", 53: "Bruine modérée", 55: "Bruine dense",
    61: "Pluie légère", 63: "Pluie modérée", 65: "Pluie forte",
    71: "Neige légère", 73: "Neige modérée", 75: "Neige forte",
    80: "Averses légères", 81: "Averses modérées", 82: "Averses fortes",
    95: "Orage", 96: "Orage avec grêle", 99: "Orage fort avec grêle",
}


def get_connection():
    """Connexion à PostgreSQL"""
    import sys
    sys.path.insert(0, '..')
    from config.db_config import DB_CONFIG
    return psycopg2.connect(**DB_CONFIG)


def fetch_weather_for_region(region_name, coords):
    """
    Appelle l'API Open-Meteo pour une région donnée
    API gratuite : https://open-meteo.com/
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "precipitation",
            "surface_pressure",
            "cloud_cover",
        ],
        "timezone": "Europe/Paris",
        "forecast_days": 1,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        wmo_code = current.get("weather_code", 0)

        return {
            "region": region_name,
            "ville_reference": coords["ville"],
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "temperature": current.get("temperature_2m"),
            "temperature_ressentie": current.get("apparent_temperature"),
            "humidite": current.get("relative_humidity_2m"),
            "vitesse_vent": current.get("wind_speed_10m"),
            "direction_vent": current.get("wind_direction_10m"),
            "precipitation": current.get("precipitation"),
            "pression": current.get("surface_pressure"),
            "couverture_nuageuse": current.get("cloud_cover"),
            "code_meteo": wmo_code,
            "description_meteo": WMO_CODES.get(wmo_code, "Inconnu"),
            "timestamp_collecte": datetime.now(),
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur API pour {region_name}: {e}")
        return None


def fetch_all_regions():
    """Récupère la météo pour toutes les régions"""
    results = []
    for region_name, coords in REGIONS_METEO.items():
        logger.info(f"🌤️  Collecte météo: {region_name} ({coords['ville']})")
        data = fetch_weather_for_region(region_name, coords)
        if data:
            results.append(data)
            logger.info(f"   → {data['temperature']}°C, {data['description_meteo']}")
        time.sleep(0.5)  # Respect rate limit API
    return results


def insert_weather(weather_data):
    """Insère les données météo dans PostgreSQL"""
    conn = get_connection()
    cur = conn.cursor()

    insert_query = """
        INSERT INTO meteo (
            region, ville_reference, latitude, longitude,
            temperature, temperature_ressentie, humidite,
            vitesse_vent, direction_vent, precipitation, pression,
            couverture_nuageuse, code_meteo, description_meteo,
            timestamp_collecte
        ) VALUES (
            %(region)s, %(ville_reference)s, %(latitude)s, %(longitude)s,
            %(temperature)s, %(temperature_ressentie)s, %(humidite)s,
            %(vitesse_vent)s, %(direction_vent)s, %(precipitation)s, %(pression)s,
            %(couverture_nuageuse)s, %(code_meteo)s, %(description_meteo)s,
            %(timestamp_collecte)s
        )
    """

    try:
        cur.executemany(insert_query, weather_data)
        conn.commit()
        logger.info(f"✅ {len(weather_data)} enregistrements météo insérés")
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erreur insertion météo: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    logger.info("🌍 Démarrage collecte météo toutes régions...")
    weather_data = fetch_all_regions()
    if weather_data:
        insert_weather(weather_data)
        logger.info(f"✅ Collecte terminée : {len(weather_data)}/12 régions")
    else:
        logger.warning("⚠️ Aucune donnée collectée")
