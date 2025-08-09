from functools import wraps
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Student
from .utils import _handle_api_token_refresh

logger = logging.getLogger(__name__)

def custom_login_required_with_token_refresh(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        print("=== DECORATOR CALLED ===")  # Debug uchun print
        # Debug uchun session ma'lumotlarini log qilish
        logger.info(f"Decorator called - Session keys: {list(request.session.keys())}")
        logger.info(f"is_admin_user: {request.session.get('is_admin_user')}")
        logger.info(f"admin_user_id: {request.session.get('admin_user_id')}")
        logger.info(f"student_db_id: {request.session.get('student_db_id')}")
        
        # Admin foydalanuvchini tekshirish
        if request.session.get('is_admin_user') and request.session.get('admin_user_id'):
            try:
                admin_user = User.objects.get(pk=request.session['admin_user_id'], is_staff=True)
                request.current_admin = admin_user
                request.current_student = None  # Admin uchun student yo'q
                logger.info(f"Admin user {admin_user.username} authenticated successfully via decorator")
                print(f"=== ADMIN AUTHENTICATED: {admin_user.username} ===")  # Debug
                return view_func(request, *args, **kwargs)
            except User.DoesNotExist:
                logger.error(f"Admin user with ID {request.session['admin_user_id']} not found or not staff")
                request.session.flush()
                messages.error(request, "Admin sessiyasi yaroqsiz. Iltimos, qayta kiring.")
                return redirect(reverse('login'))
        
        # Oddiy talaba foydalanuvchini tekshirish
        student_db_id_in_session = request.session.get('student_db_id')
        api_token_in_session = request.session.get('api_token')

        if not api_token_in_session or not student_db_id_in_session:
            messages.warning(request, "Iltimos, davom etish uchun tizimga kiring.")
            login_url_name = reverse('login')
            current_path = request.get_full_path()
            return redirect(f'{login_url_name}?next={current_path}')
        
        try:
            request.current_student = Student.objects.get(pk=student_db_id_in_session)
            request.current_admin = None  # Talaba uchun admin yo'q
        except Student.DoesNotExist:
            request.session.flush()
            messages.error(request, "Sessiya yaroqsiz yoki foydalanuvchi topilmadi. Iltimos, qayta kiring.")
            return redirect(reverse('login'))

        if not _handle_api_token_refresh(request):
            return redirect(reverse('login'))
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view