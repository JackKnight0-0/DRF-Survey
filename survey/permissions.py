from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOfSurvey(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.owner


class IsSurveyDraft(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.published
