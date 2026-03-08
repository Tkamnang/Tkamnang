"""
Scheduler principal - s'exécute toutes les 10 heures
Lance la collecte météo et la génération de données
Compatible Windows (Task Scheduler) et Linux (cron)
"""

import schedule
import time
import logging
import subprocess
import sys
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script_name):
    """Exécute un script Python et retourne True si succès"""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    logger.info(f"▶️  Exécution de {script_name}...")
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR
        )
        if result.returncode == 0:
            logger.info(f"✅ {script_name} terminé avec succès")
            if result.stdout:
                logger.info(result.stdout)
        else:
            logger.error(f"❌ {script_name} a échoué")
            logger.error(result.stderr)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"❌ Impossible d'exécuter {script_name}: {e}")
        return False


def job_collecte_complete():
    """Job principal : collecte météo toutes les 10 heures"""
    logger.info("=" * 60)
    logger.info(f"🕐 DÉMARRAGE COLLECTE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # 1. Collecte météo (toutes les 10h)
    success_meteo = run_script("fetch_weather.py")

    # 2. Nouvelles données utilisateurs (toutes les 10h)
    success_data = run_script("generate_data.py")

    if success_meteo and success_data:
        logger.info("🎉 Cycle complet terminé avec succès")
    else:
        logger.warning("⚠️ Cycle terminé avec des erreurs")

    logger.info("=" * 60)


def job_meteo_seulement():
    """Job météo uniquement (peut être lancé plus fréquemment)"""
    logger.info(f"🌤️  Collecte météo - {datetime.now().strftime('%H:%M:%S')}")
    run_script("fetch_weather.py")


if __name__ == "__main__":
    logger.info("🚀 Démarrage du scheduler...")
    logger.info("📅 Fréquence : toutes les 10 heures")

    # Exécution immédiate au démarrage
    logger.info("⚡ Première exécution immédiate...")
    job_collecte_complete()

    # Planification toutes les 10 heures
    schedule.every(10).hours.do(job_collecte_complete)

    # Optionnel : météo seule toutes les 2h pour plus de granularité
    # schedule.every(2).hours.do(job_meteo_seulement)

    logger.info("⏳ Scheduler actif. Appuyez sur Ctrl+C pour arrêter.")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Vérifie chaque minute
