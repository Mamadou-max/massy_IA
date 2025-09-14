from datetime import datetime, timedelta
from flask import Blueprint, request, current_app, render_template
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from backend.extensions import db
from backend.models import User, UserRole
from backend.utils.security import validate_password, validate_email
from backend.utils.helpers import create_response, error_response

# Blueprint API (pour les endpoints JSON)
auth_bp = Blueprint('api/auth', __name__ , url_prefix="/api/auth")

# -------------------------------
# Pages GET : Login & Register (affichage)
# -------------------------------

@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Affiche la page de connexion"""
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET'])
def register_page():
    """Affiche la page d'inscription"""
    return render_template('auth/register.html')


# -------------------------------
# Enregistrement d'un utilisateur
# -------------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name', 'role']
        if not data or not all(field in data for field in required_fields):
            return error_response("Données manquantes", 400)

        # Nettoyage et validation
        email = data['email'].strip().lower()
        username = data['username'].strip()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        role = data['role'].strip().lower()

        if not validate_email(email):
            return error_response("Format d'email invalide", 400)

        is_valid, message = validate_password(password)
        if not is_valid:
            return error_response(message, 400)

        try:
            user_role = UserRole(role)
        except ValueError:
            return error_response("Rôle invalide. Choix possibles: citizen, police, university", 400)

        # Vérification des doublons
        if User.query.filter_by(email=email).first():
            return error_response("Un utilisateur avec cet email existe déjà", 409)
        if User.query.filter_by(username=username).first():
            return error_response("Ce nom d'utilisateur est déjà pris", 409)

        # Création de l'utilisateur
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=user_role,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Création des tokens JWT
        claims = {'role': user.role.value, 'username': user.username, 'email': user.email}
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=2),
            additional_claims=claims
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=7),
            additional_claims=claims
        )

        return create_response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, "Utilisateur créé avec succès", 201)

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur inscription: {str(e)}")
        return error_response("Erreur lors de la création de l'utilisateur", 500)


# -------------------------------
# Connexion
# -------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return error_response("Email et mot de passe requis", 400)

        email = data['email'].strip()
        password = data['password']

        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not user.check_password(password):
            return error_response("Email ou mot de passe incorrect", 401)

        user.last_login = datetime.utcnow()
        db.session.commit()

        claims = {'role': user.role.value, 'username': user.username, 'email': user.email}
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=2),
            additional_claims=claims
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            expires_delta=timedelta(days=7),
            additional_claims=claims
        )

        return create_response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }, "Connexion réussie")

    except Exception as e:
        current_app.logger.error(f"Erreur connexion: {str(e)}")
        return error_response("Erreur lors de la connexion", 500)


# -------------------------------
# Rafraîchissement du token
# -------------------------------
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        access_token = create_access_token(
            identity=current_user_id,
            expires_delta=timedelta(hours=2),
            additional_claims=claims
        )
        return create_response({'access_token': access_token}, "Token rafraîchi avec succès")

    except Exception as e:
        current_app.logger.error(f"Erreur rafraîchissement token: {str(e)}")
        return error_response("Erreur lors du rafraîchissement du token", 500)


# -------------------------------
# Déconnexion
# -------------------------------
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # Déconnexion côté client seulement (pas de blacklist)
        return create_response({}, "Déconnexion réussie")
    except Exception as e:
        current_app.logger.error(f"Erreur déconnexion: {str(e)}")
        return error_response("Erreur lors de la déconnexion", 500)


# -------------------------------
# Infos utilisateur connecté
# -------------------------------
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return error_response("Utilisateur non trouvé", 404)
        return create_response({'user': user.to_dict()}, "Profil récupéré avec succès")
    except Exception as e:
        current_app.logger.error(f"Erreur récupération profil: {str(e)}")
        return error_response("Erreur lors de la récupération du profil", 500)


# -------------------------------
# Profil utilisateur par ID
# -------------------------------
@auth_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_profile(user_id):
    current_user = User.query.get(get_jwt_identity())
    if str(current_user.id) != user_id and not current_user.has_role(UserRole.POLICE):
        return error_response("Accès interdit", 403)

    data = request.get_json()
    current_user.first_name = data.get("first_name", current_user.first_name)
    current_user.last_name = data.get("last_name", current_user.last_name)
    db.session.commit()

    return create_response({'user': current_user.to_dict()}, "Profil mis à jour")



# -------------------------------
# Liste des utilisateurs
# -------------------------------
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user.has_role(UserRole.POLICE):
            return error_response("Accès réservé aux forces de l'ordre", 403)

        users = User.query.order_by(User.created_at.desc()).all()
        return create_response({
            'users': [user.to_public_dict() for user in users],
            'count': len(users)
        }, "Liste des utilisateurs récupérée")

    except Exception as e:
        current_app.logger.error(f"Erreur liste utilisateurs: {str(e)}")
        return error_response("Erreur lors de la récupération de la liste", 500)
