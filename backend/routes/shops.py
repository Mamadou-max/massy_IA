"""
Routes pour la recherche et la récupération des boutiques à Massy via Google Places.
Compatible avec le JS frontend fourni.
"""

from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from backend.utils.helpers import create_response, error_response
import requests
import os

shops_bp = Blueprint('shops', __name__, url_prefix='/api/shops')

GOOGLE_PLACES_API_KEY = "AIzaSyDSSD0AZXvKFNTyxwjTmz9zUfFJ9LkzUg4"


@shops_bp.route('/nearby', methods=['GET'])
@jwt_required(optional=True)
def get_nearby_shops():
    """Récupère les boutiques à proximité de Massy"""
    try:
        if not GOOGLE_PLACES_API_KEY:
            return error_response("Clé Google Places manquante", 500)

        lat = float(request.args.get('lat', 48.735))
        lng = float(request.args.get('lng', 2.29))
        radius = int(request.args.get('radius', 1000))
        shop_type = request.args.get('type', 'store')

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': shop_type,
            'key': GOOGLE_PLACES_API_KEY
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        shops = []
        for place in data.get('results', []):
            # Récupération des détails pour chaque boutique
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                'place_id': place['place_id'],
                'fields': 'name,rating,formatted_phone_number,website,opening_hours,geometry',
                'key': GOOGLE_PLACES_API_KEY
            }
            details_response = requests.get(details_url, params=details_params)
            details_response.raise_for_status()
            details = details_response.json().get('result', {})

            shops.append({
                'id': place['place_id'],
                'name': place.get('name', ''),
                'types': place.get('types', []),
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'address': place.get('vicinity', ''),
                'rating': details.get('rating', 0),
                'phone': details.get('formatted_phone_number', ''),
                'website': details.get('website', ''),
                'is_open': details.get('opening_hours', {}).get('open_now') if details.get('opening_hours') else None
            })

        return create_response({'shops': shops}, f"{len(shops)} boutique(s) récupérée(s) à proximité")

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erreur API Google Places: {str(e)}")
        return error_response("Service Google Places indisponible", 503)
    except Exception as e:
        current_app.logger.error(f"Erreur interne: {str(e)}")
        return error_response("Erreur interne lors de la récupération des boutiques", 500)


@shops_bp.route('/search', methods=['GET'])
@jwt_required(optional=True)
def search_shops():
    """Recherche des boutiques par nom ou type"""
    try:
        if not GOOGLE_PLACES_API_KEY:
            return error_response("Clé Google Places manquante", 500)

        query = request.args.get('query', '').strip()
        if not query:
            return create_response({'shops': []}, "Aucun résultat pour la recherche")

        lat = float(request.args.get('lat', 48.735))
        lng = float(request.args.get('lng', 2.29))

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': query,
            'location': f"{lat},{lng}",
            'radius': 5000,
            'key': GOOGLE_PLACES_API_KEY
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        shops = []
        for place in data.get('results', []):
            shops.append({
                'id': place.get('place_id', ''),
                'name': place.get('name', ''),
                'types': place.get('types', []),
                'address': place.get('formatted_address', ''),
                'rating': place.get('rating', 0),
                'lat': place['geometry']['location']['lat'],
                'lng': place['geometry']['location']['lng'],
                'icon': place.get('icon', '')
            })

        return create_response({'shops': shops}, f"{len(shops)} boutique(s) trouvée(s) pour la recherche '{query}'")

    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erreur API Google Places: {str(e)}")
        return error_response("Service Google Places indisponible", 503)
    except Exception as e:
        current_app.logger.error(f"Erreur interne: {str(e)}")
        return error_response("Erreur interne lors de la recherche de boutiques", 500)
