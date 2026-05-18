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
                print(f" Permission refusée : utilisateur non authentifié")
            return False
        
        # 2. Vérifier le rôle (tolère 'EXPERT', 'expert', 'Expert')
        user_role = getattr(request.user, 'role', None)
        role_upper = str(user_role).upper() if user_role else None
        is_expert = role_upper == 'EXPERT'
        
        # Debug détaillé en développement
        if settings.DEBUG:
            print(f" [IsExpert] Debug:")
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
    Lecture publique, écriture réservée aux authentifiés.
    Utilisé pour les offres : tout le monde peut consulter, seuls les connectés voient les détails.
    """
    
    def has_permission(self, request, view):
        # Lecture (GET, HEAD, OPTIONS) : toujours autorisé
        if request.method in permissions.SAFE_METHODS:
            return True
        # Écriture : doit être authentifié
        return request.user and request.user.is_authenticated


class IsVisitorOrAuthenticated(permissions.BasePermission):
    """Autorise les visiteurs ET les utilisateurs authentifiés (pour newsletter, etc.)"""
    
    def has_permission(self, request, view):
        return True  # Toujours autorisé