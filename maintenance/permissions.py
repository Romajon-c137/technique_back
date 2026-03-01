from rest_framework import permissions


class IsMaintenanceResponsibleOrAssigned(permissions.BasePermission):
    """
    Доступ к инстансу ТО имеют:
    - Ответственный за технику (equipment.responsible)
    - Назначенный исполнитель (assigned_to)
    - Суперпользователи
    """
    
    def has_object_permission(self, request, view, obj):
        # Суперпользователи имеют полный доступ
        if request.user.is_superuser:
            return True
        
        # Ответственный за технику
        if obj.equipment.responsible == request.user:
            return True
        
        # Назначенный исполнитель
        if obj.assigned_to == request.user:
            return True
        
        return False


class CanPerformMaintenance(permissions.BasePermission):
    """
    Выполнять ТО может любой пользователь
    (фиксируется в completed_by кто реально сделал)
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Любой аутентифицированный пользователь может выполнить ТО
        return request.user.is_authenticated
