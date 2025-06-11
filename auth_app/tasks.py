# auth_app/tasks.py
from celery import shared_task
from django.conf import settings
from django.utils import timezone # timezone ni import qilish
import logging

from .services.hemis_api_service import HemisAPIClient, APIClientException
from .models import Student
from .utils import map_api_data_to_student_model_defaults, update_student_instance_with_defaults # <--- YANGI IMPORTLAR

logger = logging.getLogger(__name__)

# Vazifa nomini o'zgartirdim, chunki oldingi nom fayl nomi bilan bir xil edi
@shared_task(bind=True, name='auth_app.tasks.sync_student_profile_from_api', max_retries=3, default_retry_delay=60 * 5) 
def sync_student_profile_from_api(self, student_id, api_token=None):
    """
    Talaba profilini API dan olib, DBga asinxron tarzda yangilaydi.
    Bu Celery vazifasi.
    `api_token` berilishi kerak. Agar ma'muriy token bilan ishlash kerak bo'lsa,
    HemisAPIClient da alohida metod va sozlama kerak.
    """
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        logger.error(f"Student with ID {student_id} not found in Celery task. Task will not retry.")
        return f"Student ID {student_id} not found." # Qayta urinish shart emas

    # Bu task odatda studentning o'z tokeni bilan (login paytida yoki boshqa triggerda)
    # yoki ma'muriy token bilan (davriy yangilash uchun) chaqirilishi mumkin.
    # Hozirgi implementatsiya `api_token` berilishini talab qiladi.
    
    effective_api_token = api_token
    api_source_description = f"provided token for student {student.username}"

    if not effective_api_token:
        # Agar student uchun saqlangan token bo'lsa (masalan, shifrlangan holda)
        # uni olish logikasi bu yerda bo'lishi mumkin. Lekin bu xavfsizlikka zid.
        # Eng yaxshi variant - task chaqirilganda yaroqli token berish.
        # Yoki, agar ma'muriy vazifa bo'lsa:
        if hasattr(settings, 'HEMIS_SYSTEM_API_TOKEN') and settings.HEMIS_SYSTEM_API_TOKEN:
             effective_api_token = settings.HEMIS_SYSTEM_API_TOKEN
             api_source_description = f"system token for student {student.username} (ID: {student.student_id_number or student.username})"
             # BU YERDA MUHIM: HEMIS_SYSTEM_API_TOKEN bilan client.get_account_me() emas,
             # balki client.get_student_info_by_id(student.student_id_number) kabi metod chaqirilishi kerak.
             # Hozircha, get_account_me() ishlatiladi, bu esa system token kimga tegishli bo'lsa,
             # o'sha foydalanuvchi ma'lumotini oladi. BU XATO BO'LISHI MUMKIN.
             # Agar API student ma'lumotini IDsi bo'yicha olishga ruxsat bersa, shuni ishlatish kerak.
             logger.warning(f"Using HEMIS_SYSTEM_API_TOKEN for task, but get_account_me() might fetch system user's data, not student's, unless API is specifically designed for it or client uses student_id_number with this token.")
        else:
            logger.error(f"No API token provided for student ID {student_id} (username: {student.username}) in Celery task, and no system token configured.")
            return f"API token required for student ID {student_id}."
            
    try:
        client = HemisAPIClient(api_token=effective_api_token)
        
        # Agar HEMIS_SYSTEM_API_TOKEN ishlatilayotgan bo'lsa va API clientda shunday metod bo'lsa:
        # if effective_api_token == getattr(settings, 'HEMIS_SYSTEM_API_TOKEN', None) and hasattr(client, 'get_student_info_by_id_number'):
        #     student_info_from_api = client.get_student_info_by_id_number(student.student_id_number or student.username)
        # else:
        #     student_info_from_api = client.get_account_me() # Joriy token egasining ma'lumotini oladi

        # Hozircha oddiyroq:
        student_info_from_api = client.get_account_me()


        if student_info_from_api and isinstance(student_info_from_api, dict):
            defaults = map_api_data_to_student_model_defaults(
                student_info_from_api, 
                student.username # Yoki student.student_id_number, agar u asosiy identifikator bo'lsa
            )
            if defaults:
                update_student_instance_with_defaults(student, defaults)
                logger.info(f"Successfully updated profile using {api_source_description} via Celery task.")
                return f"Student ID {student_id} updated."
            else:
                logger.warning(f"Could not map API data for student ID {student_id} in Celery task. API data: {str(student_info_from_api)[:200]}")
                return f"Failed to map API data for student ID {student_id}."
        elif not student_info_from_api:
            logger.warning(f"No data received from API for student ID {student_id} (username: {student.username}) using {api_source_description} in Celery task.")
            return f"No API data for student ID {student_id}."
        else:
            logger.warning(f"Received non-dict data from API for student ID {student_id} using {api_source_description} in Celery task: {str(student_info_from_api)[:100]}")
            return f"Invalid API data type for student ID {student_id}."
            
    except APIClientException as e:
        logger.error(f"APIClientException for student ID {student_id} (username: {student.username}) using {api_source_description} in Celery task: {e.args[0]} (Status: {e.status_code})", exc_info=True)
        try:
            # Token bilan bog'liq xatolik bo'lsa (401, 403), qayta urinish foydasiz bo'lishi mumkin.
            if e.status_code in [401, 403]:
                logger.warning(f"Token-related API error ({e.status_code}) for student {student.username}. Not retrying.")
                return f"Token error for student {student.username}."
            raise self.retry(exc=e, countdown=int(self.default_retry_delay * (2 ** self.request.retries)))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for student ID {student_id} (username: {student.username}) in Celery task after APIClientException.")
            return f"Max retries for student {student.username} (APIClientException)."
    except Exception as e:
        logger.error(f"Unexpected error updating student ID {student_id} (username: {student.username}) using {api_source_description} in Celery task: {e}", exc_info=True)
        try:
            raise self.retry(exc=e, countdown=int(self.default_retry_delay * (2 ** self.request.retries)))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for student ID {student_id} (username: {student.username}) (unexpected error) in Celery task.")
            return f"Max retries for student {student.username} (unexpected error)."