# offres/permissions.py
from rest_framework import permissions

class IsProfileComplete(permissions.BasePermission):
    """Vérifie que l'utilisateur a complété son profil selon son rôle."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'EXPERT':
            return hasattr(request.user, 'profil_expert') and request.user.profil_expert.cv_fichier
        elif request.user.role == 'BUREAU':
            return hasattr(request.user, 'bureauetude')
        return True  # VISITEUR ou ADMIN

class IsExpert(permissions.BasePermission):
    """Accès réservé aux Experts avec profil complet"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role == 'EXPERT' and 
                IsProfileComplete().has_permission(request, view))

class IsBureau(permissions.BasePermission):
    """Accès réservé aux Bureaux avec profil complet"""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role == 'BUREAU' and 
                IsProfileComplete().has_permission(request, view))

class IsAdmin(permissions.BasePermission):
    """Accès réservé aux Administrateurs"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsAuthenticatedOrReadOnlyPublic(permissions.BasePermission):
    """Lecture publique autorisée, écriture réservée aux authentifiés."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

class IsVisitorOrAuthenticated(permissions.BasePermission):
    """Permet l'accès public aux offres/newsletter, et privé aux connectés."""
    def has_permission(self, request, view):
        if view.basename in ['offres', 'newsletter'] and request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated