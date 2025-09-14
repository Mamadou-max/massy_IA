from flask import Blueprint, request
import requests
from bs4 import BeautifulSoup
from backend.utils.helpers import create_response, error_response

news_bp = Blueprint('news', __name__, url_prefix='/api/news')


@news_bp.route('/', methods=['GET'])
def get_news():
    """
    Scraper les actualités locales de Massy et renvoyer directement au frontend.
    Filtrage par catégorie si nécessaire.
    """
    category_filter = request.args.get('category', 'all').lower()

    try:
        url = "https://www.massy.fr/nav-newsactus"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        news_list = []

        # Scrape jusqu'à 20 articles pour filtrer
        for article in soup.select('.news-item')[:20]:
            title_elem = article.select_one('.title')
            link_elem = article.select_one('a')
            date_elem = article.select_one('.date')
            category_elem = article.select_one('.category')  # si le site a un élément category

            news_category = category_elem.text.strip().lower() if category_elem else "general"

            # Filtrage
            if category_filter != "all" and news_category != category_filter:
                continue

            news_list.append({
                "title": title_elem.text.strip() if title_elem else "Titre inconnu",
                "url": link_elem['href'] if link_elem and link_elem.has_attr('href') else "#",
                "category": news_category,
                "source": "Massy.fr",
                "date": date_elem.text.strip() if date_elem else None,
                "tags": []
            })

        return create_response({"news_items": news_list}, f"{len(news_list)} actualité(s) récupérée(s)")

    except requests.RequestException as e:
        return error_response(f"Erreur réseau: {str(e)}", 503)
    except Exception as e:
        return error_response(f"Erreur récupération news: {str(e)}", 500)
