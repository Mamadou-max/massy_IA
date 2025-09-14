# backend/scripts/auto_sync.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
from apscheduler.schedulers.background import BackgroundScheduler

from backend.extensions import db
from backend.models.urbanism_project import UrbanismProject   # ✅ CORRECT
from backend.models.suspect_alert import SuspectAlert         # ✅ CORRECT
from backend.models.research_project import ResearchProject   # ✅ CORRECT


def sync_urbanism():
    """Synchronise les projets UrbanismProject avec les événements Massy"""
    try:
        url = "https://www.ville-massy.fr/agenda"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        events = soup.select(".event-card")

        added = 0
        for e in events:
            title = e.select_one(".event-title").get_text(strip=True) if e.select_one(".event-title") else None
            if not title:
                continue

            # Empêcher les doublons
            if UrbanismProject.query.filter_by(title=title).first():
                continue

            description = e.select_one(".event-description").get_text(strip=True) if e.select_one(".event-description") else "Aucune description"
            date_str = e.select_one(".event-date").get_text(strip=True) if e.select_one(".event-date") else None

            date_parsed = datetime.utcnow()
            if date_str:
                try:
                    date_parsed = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    pass

            new_event = UrbanismProject(
                title=title,
                description=description,
                created_at=date_parsed,
                updated_at=date_parsed
            )
            db.session.add(new_event)
            added += 1

        db.session.commit()
        print(f"[SYNC] UrbanismProject: {added} nouveaux projets ajoutés.")
    except Exception as e:
        print(f"[SYNC ERROR] UrbanismProject: {e}")


def sync_suspect_alerts():
    """Ajoute des alertes fictives si la table est vide"""
    try:
        if SuspectAlert.query.count() == 0:
            samples = [
                {"type": "Intrusion", "desc": "Détection d'une intrusion sur site", "risk": 7},
                {"type": "Incendie", "desc": "Début d'incendie détecté", "risk": 9},
                {"type": "Comportement suspect", "desc": "Individu observé en zone sensible", "risk": 5}
            ]
            for s in samples:
                alert = SuspectAlert(
                    alert_type=s["type"],
                    description=s["desc"],
                    latitude=48.726 + random.uniform(-0.01, 0.01),
                    longitude=2.283 + random.uniform(-0.01, 0.01),
                    risk_level=s["risk"],
                    status="new",
                    reported_at=datetime.utcnow(),
                    user_id="00000000-0000-0000-0000-000000000001"
                )
                db.session.add(alert)
            db.session.commit()
            print("[SYNC] SuspectAlert: alertes fictives ajoutées.")
    except Exception as e:
        print(f"[SYNC ERROR] SuspectAlert: {e}")


def sync_research_projects():
    """Ajoute des projets fictifs si table vide"""
    try:
        if ResearchProject.query.count() == 0:
            samples = [
                {"title": "Analyse du trafic", "desc": "Étude sur la fluidité des routes", "status": "in_progress"},
                {"title": "Étude sécurité", "desc": "Analyse des incidents survenus en 2024", "status": "in_progress"}
            ]
            for s in samples:
                rp = ResearchProject(
                    title=s["title"],
                    description=s["desc"],
                    status=s["status"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    user_id="00000000-0000-0000-0000-000000000001"
                )
                db.session.add(rp)
            db.session.commit()
            print("[SYNC] ResearchProject: projets ajoutés.")
    except Exception as e:
        print(f"[SYNC ERROR] ResearchProject: {e}")


def auto_sync_all():
    """Lance toutes les synchronisations"""
    print("[SYNC] Lancement de la synchronisation automatique...")
    sync_urbanism()
    sync_suspect_alerts()
    sync_research_projects()
    print("[SYNC] Synchronisation terminée.")


def start_scheduler(app):
    """Démarre le scheduler en arrière-plan"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: run_with_context(app), trigger="interval", minutes=30)
    scheduler.start()
    print("[SCHEDULER] Synchronisation programmée toutes les 30 minutes.")


def run_with_context(app):
    with app.app_context():
        auto_sync_all()
