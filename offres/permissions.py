# offres/permissions.py
from rest_framework import permissions
from django.conf import settings

class IsExpert(permissions.BasePermission):
    """
    Permission réservée aux utilisateurs de rôle EXPERT.
    Tolère les variations de casse et loggue les échecs en DEBUG.
    """
    
    def has_permission(self, request, view):
        # 1. Doit être authentifié
        if not request.user or not request.user.is_authenticated:
            if settings.DEBUG:
                print(f"❌ Permission refusée : utilisateur non authentifié")
            return False
        
        # 2. Vérifier le rôle (tolère 'EXPERT', 'expert', 'Expert')
        user_role = getattr(request.user, 'role', None)
        role_upper = str(user_role).upper() if user_role else None
        is_expert = role_upper == 'EXPERT'
        
        # Debug détaillé en développement
        if settings.DEBUG:
            print(f"🔍 [IsExpert] Debug:")
            print(f"    User: {request.user.email if hasattr(request.user, 'email') else request.user}")
            print(f"    Role brut: '{user_role}'")
            print(f"    Role upper: '{role_upper}'")
            print(f"    Is expert: {is_expert}")
        
        return is_expert


class IsBureau(permissions.BasePermission):
    """Permission réservée aux bureaux d'études"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, 'role', None)
        return user_role and str(user_role).upper() in ['BUREAU', 'BUREAU_ETUDE']


class IsAdmin(permissions.BasePermission):
    """Permission réservée aux administrateurs"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsAuthenticatedOrReadOnlyPublic(permissions.BasePermission):
    """
    ✅ CORRIGÉ : Lecture publique, écriture réservée aux authentifiés.
    Utilisé pour les offres : tout le monde peut consulter.
    """
    
    def has_permission(self, request, view):
        # Lecture (GET, HEAD, OPTIONS) : toujours autorisé
        if request.method in permissions.SAFE_METHODS:
            return True
        # Écriture : doit être authentifié
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Permission sur l'objet lui-même"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsVisitorOrAuthenticated(permissions.BasePermission):
    """
    ✅ AJOUTÉ : Autorise les visiteurs NON connectés (lecture) ET les utilisateurs authentifiés.
    Pour newsletter, consultation d'offres, etc.
    """
    
    def has_permission(self, request, view):
        # Lecture : toujours autorisé (visiteur ou authentifié)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Écriture : nécessite authentification
        return request.user and request.user.is_authenticated


class IsVisitor(permissions.BasePermission):
    """
    ✅ AJOUTÉ : Permission pour les visiteurs non connectés
    - Consultation des offres (lecture seule)
    - Inscription newsletter
    """
    def has_permission(self, request, view):
        # Lecture publique autorisée
        if request.method in permissions.SAFE_METHODS:
            return True
        return False