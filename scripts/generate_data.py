"""
Script de génération de données aléatoires
Génère des personnes avec : nom, adresse, âge, problèmes, doublons, solutions
"""

import random
import psycopg2
from faker import Faker
from datetime import datetime, timedelta
import logging
import os
import sys


# Ajouter le dossier parent au path pour trouver config

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Régions françaises avec leurs coordonnées approximatives
REGIONS_FRANCE = {
    "Île-de-France":        {"lat": 48.8566, "lon": 2.3522},
    "Auvergne-Rhône-Alpes": {"lat": 45.7640, "lon": 4.8357},
    "Provence-Alpes-Côte d'Azur": {"lat": 43.9352, "lon": 6.0679},
    "Nouvelle-Aquitaine":   {"lat": 44.8400, "lon": -0.5800},
    "Occitanie":            {"lat": 43.6047, "lon": 1.4442},
    "Hauts-de-France":      {"lat": 50.6292, "lon": 3.0573},
    "Grand Est":            {"lat": 48.6921, "lon": 6.1844},
    "Normandie":            {"lat": 49.1829, "lon": 0.3707},
    "Bretagne":             {"lat": 48.2020, "lon": -2.9326},
    "Pays de la Loire":     {"lat": 47.4784, "lon": -0.5632},
    "Centre-Val de Loire":  {"lat": 47.7516, "lon": 1.6751},
    "Bourgogne-Franche-Comté": {"lat": 47.2805, "lon": 4.9994},
}

PROBLEMES = [
    "Connexion internet instable",
    "Erreur de facturation",
    "Produit défectueux",
    "Retard de livraison",
    "Service client inaccessible",
    "Application qui plante",
    "Mot de passe oublié",
    "Commande annulée sans raison",
    "Remboursement non reçu",
    "Données personnelles incorrectes",
    "Double prélèvement bancaire",
    "Colis perdu",
    "Compte bloqué",
    "Erreur dans la commande",
    "Problème d'inscription",
]

SOLUTIONS = [
    "Réinitialisation du système effectuée",
    "Remboursement intégral accordé",
    "Remplacement du produit envoyé",
    "Bon de réduction de compensation offert",
    "Escalade vers l'équipe technique",
    "Mise à jour logicielle appliquée",
    "Réinitialisation du mot de passe envoyée par email",
    "Commande recréée et prioritaire",
    "Virement de remboursement initié sous 48h",
    "Correction des données dans le système",
    "Annulation du double prélèvement confirmée",
    "Enquête de transport ouverte",
    "Déblocage manuel du compte effectué",
    "Correction de commande traitée",
    "Aide à l'inscription par l'équipe support",
]

STATUTS = ["Ouvert", "En cours", "Résolu", "Fermé"]


def get_connection():
    """Connexion à PostgreSQL"""
    from config.db_config import DB_CONFIG
    return psycopg2.connect(**DB_CONFIG)


def generate_persons(n=200):
    """Génère n personnes fictives"""
    fake = Faker('fr_FR')
    persons = []

    for i in range(n):
        region = random.choice(list(REGIONS_FRANCE.keys()))
        coords = REGIONS_FRANCE[region]

        # Variation légère des coordonnées pour répartir dans la région
        lat = coords["lat"] + random.uniform(-1.5, 1.5)
        lon = coords["lon"] + random.uniform(-1.5, 1.5)

        probleme = random.choice(PROBLEMES)
        solution = random.choice(SOLUTIONS) if random.random() > 0.3 else None
        statut = random.choice(STATUTS)
        if solution:
            statut = random.choice(["Résolu", "Fermé"])
        else:
            statut = random.choice(["Ouvert", "En cours"])

        person = {
            "nom": fake.last_name(),
            "prenom": fake.first_name(),
            "email": fake.email(),
            "telephone": fake.phone_number(),
            "adresse": fake.street_address(),
            "ville": fake.city(),
            "code_postal": fake.postcode(),
            "region": region,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "age": random.randint(18, 85),
            "probleme": probleme,
            "solution": solution,
            "statut": statut,
            "est_doublon": False,
            "date_creation": datetime.now() - timedelta(days=random.randint(0, 365)),
        }
        persons.append(person)

    # Ajout de doublons (environ 10%)
    nb_doublons = n // 10
    for _ in range(nb_doublons):
        original = random.choice(persons)
        doublon = original.copy()
        doublon["est_doublon"] = True
        doublon["email"] = original["email"]  # même email = doublon détectable
        doublon["date_creation"] = original["date_creation"] + timedelta(hours=random.randint(1, 48))
        persons.append(doublon)

    logger.info(f"✅ {n} personnes générées + {nb_doublons} doublons = {len(persons)} total")
    return persons


def insert_persons(persons):
    """Insère les personnes dans PostgreSQL"""
    conn = get_connection()
    cur = conn.cursor()

    insert_query = """
        INSERT INTO persons (
            nom, prenom, email, telephone, adresse, ville, code_postal,
            region, latitude, longitude, age, probleme, solution, statut,
            est_doublon, date_creation
        ) VALUES (
            %(nom)s, %(prenom)s, %(email)s, %(telephone)s, %(adresse)s,
            %(ville)s, %(code_postal)s, %(region)s, %(latitude)s, %(longitude)s,
            %(age)s, %(probleme)s, %(solution)s, %(statut)s,
            %(est_doublon)s, %(date_creation)s
        )
    """

    try:
        cur.executemany(insert_query, persons)
        conn.commit()
        logger.info(f"✅ {len(persons)} enregistrements insérés dans PostgreSQL")
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erreur insertion: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    logger.info("🚀 Démarrage de la génération de données...")
    persons = generate_persons(200)
    insert_persons(persons)
    logger.info("✅ Génération terminée !")
