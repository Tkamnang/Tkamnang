@echo off
REM ============================================================
REM Script de setup complet du projet sous Windows
REM Double-cliquer pour lancer
REM ============================================================

echo.
echo =====================================================
echo   SETUP DU PROJET DASHBOARD
echo =====================================================
echo.

REM Vérifier Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo Telecharger Python sur https://python.org
    pause
    exit /b 1
)

echo [OK] Python detecte
python --version

REM Installer les dependances
echo.
echo [1/4] Installation des dependances Python...
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo [ERREUR] Echec installation des dependances
    pause
    exit /b 1
)
echo [OK] Dependances installees

REM Tester la connexion PostgreSQL
echo.
echo [2/4] Test connexion PostgreSQL...
python -c "from config.db_config import DB_CONFIG; import psycopg2; conn = psycopg2.connect(**DB_CONFIG); print('[OK] Connexion PostgreSQL reussie'); conn.close()"
IF ERRORLEVEL 1 (
    echo.
    echo [ERREUR] Impossible de se connecter a PostgreSQL
    echo Verifiez :
    echo   1. PostgreSQL est demarre (Services Windows)
    echo   2. Le mot de passe dans config/db_config.py est correct
    echo   3. La base 'dashboard_db' existe
    pause
    exit /b 1
)

REM Générer les données initiales
echo.
echo [3/4] Generation des donnees initiales...
cd scripts
python generate_data.py
IF ERRORLEVEL 1 (
    echo [ERREUR] Echec generation donnees
    pause
    exit /b 1
)

REM Collecte météo initiale
echo.
echo [4/4] Collecte meteo initiale...
python fetch_weather.py
IF ERRORLEVEL 1 (
    echo [ERREUR] Echec collecte meteo
    pause
    exit /b 1
)

echo.
echo =====================================================
echo   SETUP TERMINE AVEC SUCCES !
echo =====================================================
echo.
echo Prochaines etapes :
echo   1. Ouvrir Power BI Desktop
echo   2. Connecter a PostgreSQL (localhost, dashboard_db)
echo   3. Charger les vues : v_dashboard_principal, etc.
echo   4. Lancer le scheduler : python scripts/scheduler.py
echo.
pause
