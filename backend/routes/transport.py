"""
Routes pour la récupération des informations de transport (SNCF, RATP) à Massy.
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from backend.utils.helpers import create_response, error_response
import requests
from datetime import datetime

transport_bp = Blueprint('transport', __name__, url_prefix='/api/transport')

# Clé API SNCF
SNCF_API_KEY = "8c8a44bc-dde8-4e00-89cc-1d589498cb8b"


def resolve_sncf_stop_area(station_name: str):
    """Recherche le code stop_area d'une gare à partir de son nom"""
    try:
        url = "https://api.sncf.com/v1/coverage/sncf/places"
        params = {"q": station_name}
        response = requests.get(url, params=params, auth=(SNCF_API_KEY, ""))
        response.raise_for_status()
        data = response.json()

        for place in data.get("places", []):
            if place.get("embedded_type") == "stop_area":
                return place["id"]
        return None
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"[SNCF] Erreur lors de la recherche de la gare {station_name}: {e}")
        return None


@transport_bp.route('/sncf', methods=['GET'])
@jwt_required(optional=True)
def get_sncf_journeys():
    """Récupère les trajets SNCF entre deux gares avec noms exacts et durées réelles"""
    try:
        if not SNCF_API_KEY:
            return error_response("Clé API SNCF manquante. Configurez SNCF_API_KEY.", 500)

        departure_name = request.args.get('departure', 'Massy TGV')
        arrival_name = request.args.get('arrival', 'Paris Gare de Lyon')

        from_code = resolve_sncf_stop_area(departure_name)
        to_code = resolve_sncf_stop_area(arrival_name)

        if not from_code or not to_code:
            return error_response(f"Gare introuvable : {departure_name} ou {arrival_name}", 400)

        url = "https://api.sncf.com/v1/coverage/sncf/journeys"
        params = {
            'from': from_code,
            'to': to_code,
            'datetime': datetime.now().strftime("%Y%m%dT%H%M%S")
        }
        response = requests.get(url, params=params, auth=(SNCF_API_KEY, ""))
        response.raise_for_status()
        data = response.json()

        journeys = []
        for journey in data.get('journeys', [])[:5]:
            sections = []
            for section in journey.get('sections', []):
                if section.get('type') == 'public_transport':
                    sections.append({
                        'type': 'train',
                        'from': section['from']['stop_point']['name'],
                        'to': section['to']['stop_point']['name'],
                        'duration': section['duration'] // 60,
                        'mode': section['display_informations']['commercial_mode']
                    })

            journeys.append({
                'departure_time': journey['departure_date_time'].split('T')[1][:5],
                'arrival_time': journey['arrival_date_time'].split('T')[1][:5],
                'duration': journey['duration'] // 60,
                'type': 'SNCF',
                'status': 'Ponctuel' if not journey.get('disruptions') else 'Perturbé',
                'sections': sections
            })

        return create_response({'journeys': journeys}, f"{len(journeys)} trajet(s) SNCF récupéré(s)")

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erreur API SNCF: {str(e)}")
        return error_response("Service SNCF indisponible", 503)
    except Exception as e:
        current_app.logger.error(f"Erreur interne SNCF: {str(e)}")
        return error_response("Erreur interne lors de la récupération des trajets SNCF", 500)


@transport_bp.route('/ratp', methods=['GET'])
@jwt_required(optional=True)
def get_ratp_journeys():
    """Récupère les trajets RATP (métro, bus, tram) avec mapping automatique et trajets réels"""
    try:
        departure_input = request.args.get('departure', 'Massy TGV')
        arrival_input = request.args.get('arrival', 'Châtelet')

        # Mapping automatique des gares SNCF vers stations RATP valides
        station_mapping = {
            "Massy TGV": "Massy Opéra",
            "Massy-Palaiseau": "Massy Opéra",
            "Paris Gare de Lyon": "Châtelet",
            "Paris Montparnasse": "Montparnasse-Bienvenue"
        }

        departure = station_mapping.get(departure_input, departure_input)
        arrival = station_mapping.get(arrival_input, arrival_input)

        # Liste des stations RATP valides autour de Massy et Paris
        valid_stations = [
            "Massy Opéra", "Vilgénis", "Châtelet", "Montparnasse-Bienvenue",
            "Invalides", "Nation", "La Défense"
        ]

        if departure not in valid_stations or arrival not in valid_stations:
            return error_response(f"Stations RATP non valides : {departure} ou {arrival}", 400)

        url = "https://api-ratp.pierre-grimaud.fr/v4/journeys"
        params = {'from': departure, 'to': arrival}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get('result', {}).get('journeys'):
            return error_response("Aucun trajet RATP trouvé pour ces stations", 404)

        journeys = []
        for journey in data['result']['journeys'][:5]:
            sections = []
            for section in journey.get('sections', []):
                if section.get('type') == 'public_transport':
                    sections.append({
                        'type': section['display_informations']['network'],
                        'from': section['from']['name'],
                        'to': section['to']['name'],
                        'duration': section['duration'] // 60,
                        'line': section['display_informations']['code']
                    })

            journeys.append({
                'departure_time': journey['departure_date_time'].split('T')[1][:5],
                'arrival_time': journey['arrival_date_time'].split('T')[1][:5],
                'duration': journey['duration'] // 60,
                'type': 'RATP',
                'status': 'Ponctuel',
                'sections': sections
            })

        return create_response({'journeys': journeys}, f"{len(journeys)} trajet(s) RATP récupéré(s)")

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erreur API RATP: {str(e)}")
        return error_response("Service RATP indisponible", 503)
    except Exception as e:
        current_app.logger.error(f"Erreur interne RATP: {str(e)}")
        return error_response("Erreur interne lors de la récupération des trajets RATP", 500)


@transport_bp.route('/stations', methods=['GET'])
@jwt_required(optional=True)
def get_transport_stations():
    """Récupère les stations de transport autour de Massy avec coordonnées réelles"""
    try:
        stations = [
            {'name': 'Gare de Massy TGV', 'type': 'sncf', 'lat': 48.7352, 'lng': 2.2896, 'lines': ['TGV', 'TER', 'RER B', 'RER C']},
            {'name': 'Massy-Palaiseau RER', 'type': 'sncf', 'lat': 48.7324, 'lng': 2.2848, 'lines': ['RER B', 'RER C']},
            {'name': 'Massy Opéra', 'type': 'ratp', 'lat': 48.7381, 'lng': 2.2889, 'lines': ['Bus 199', 'Bus 319', 'Bus 399']},
            {'name': 'Vilgénis', 'type': 'ratp', 'lat': 48.7290, 'lng': 2.2950, 'lines': ['Bus 199']},
            {'name': 'Châtelet', 'type': 'ratp', 'lat': 48.8582, 'lng': 2.3470, 'lines': ['Metro 1', 'Metro 4', 'Metro 7', 'Metro 11', 'Metro 14']},
            {'name': 'Montparnasse-Bienvenue', 'type': 'ratp', 'lat': 48.8422, 'lng': 2.3211, 'lines': ['Metro 4', 'Metro 6', 'Metro 12', 'Metro 13']},
            {'name': 'La Défense', 'type': 'ratp', 'lat': 48.8910, 'lng': 2.2370, 'lines': ['Metro 1', 'RER A']}
        ]
        return create_response({'stations': stations}, f"{len(stations)} station(s) récupérée(s)")
    except Exception as e:
        current_app.logger.error(f"Erreur interne: {str(e)}")
        return error_response("Erreur interne lors de la récupération des stations de transport", 500)
