# auth_app/permissions.py

from rest_framework.permissions import BasePermission
from .models import SurveyResponse

class CanRespondToSurvey(BasePermission):
    """
    Foydalanuvchi so'rovnomaga javob bera olishini tekshiradi:
    1. So'rovnoma ochiq bo'lishi kerak.
    2. Talaba unga avval javob bermagan bo'lishi kerak.
    """
    message = "Siz bu so'rovnomada ishtirok eta olmaysiz yoki u yopilgan."

    def has_object_permission(self, request, view, obj):
        # `obj` bu yerda Survey instansi
        survey = obj
        student = getattr(request, 'current_student', None)

        if not student:
            self.message = "Talaba topilmadi."
            return False
            
        if not survey.is_open:
            self.message = "Bu so'rovnoma hozirda mavjud emas yoki muddati tugagan."
            return False

        if not survey.is_anonymous and SurveyResponse.objects.filter(survey=survey, student=student).exists():
            self.message = "Siz bu so'rovnomada avval ishtirok etgansiz."
            return False
        
        return True