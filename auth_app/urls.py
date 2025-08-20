# auth_app/urls.py

from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views 
from . import api_views # Yangi import
from .views import SurveyStatisticsAPIView

from django.conf import settings
from django.conf.urls.static import static
# Bu mavjud URL manzillaringiz
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.home_view, name='home'),

    path('surveys/', views.survey_list_view, name='survey_list'),
    path('surveys/<int:survey_pk>/', views.survey_detail_view, name='survey_detail'),
    path('api/surveys/<int:survey_pk>/submit/', views.submit_survey_api_view, name='submit_survey_api'),
    path('api/surveys/<int:survey_pk>/statistics/', SurveyStatisticsAPIView.as_view(), name='survey_statistics_api'),
    path('surveys/<int:survey_pk>/statistics/', views.survey_statistics_view, name='survey_statistics'),
    
    # Admin panel URLs
    path('admin-surveys/', views.admin_surveys_list, name='admin_surveys_list'),
    path('admin-surveys/<int:survey_pk>/stats/', views.survey_statistics_view, name='admin_survey_statistics'),
    path('admin-surveys/<int:survey_pk>/stats/pdf/', views.survey_statistics_pdf_view, name='survey_statistics_pdf'),
    # path('api/surveys/<int:survey_pk>/submit/<int:question_pk>/', views.submit_question_api_view, name='submit_question_api'),
    # path('api/surveys/<int:survey_pk>/submit/<int:question_pk>/<int:choice_pk>/', views.submit_choice_api_view, name='submit_choice_api'),
    # path('api/surveys/<int:survey_pk>/submit/<int:question_pk>/text/', views.submit_text_api_view, name='submit_text_api'),
    # path('api/surveys/<int:survey_pk>/submit/<int:question_pk>/multiple_choices/', views.submit_multiple_choices_api_view, name='submit_multiple_choices_api'),
    # path('api/surveys/<int:survey_pk>/submit/<int:question_pk>/file/', views.submit_file_api_view, name='submit_file_api'),
    # path('api/surveys/<int:survey_pk>/submit/<int:question_pk>/date/', views.submit_date_api_view, name='submit_date_api'),
    # path('api/surveys/<int:survey_pk>/submit/<int:question_pk>/number/', views.submit_number_api_view, name='submit_number_api'),
    # path('api/surveys/<int:survey_pk>/submit/<int:question_pk>/scale/', views.submit_scale_api_view, name='submit_scale_api'),
    # path('api/surveys/<int:survey_pk>/submit/<int:question_pk>/yes_no/', views.submit_yes_no_api_view, name='submit_yes_no_api'),

    path('responsible-persons/', views.responsible_person_list_view, name='responsible_person_list'),
    path('responsible-person/<int:person_id>/send/', views.send_message_to_responsible_view, name='send_message_to_responsible'),
    path('messages/', views.student_messages_list_view, name='student_messages_list'),
    path('messages/<int:msg_id>/', views.student_message_detail_view, name='student_message_detail'),
    path('jumpl/messages/', views.admin_messages_list_view, name='admin_messages_list'),
    path('jumpl/messages/<int:msg_id>/', views.admin_message_detail_view, name='admin_message_detail'),
]

# API uchun yangi URL manzillari
api_urlpatterns = [
    # Autentifikatsiya
    # Hozircha bu qismni commentga olamiz, chunki u to'liq ishlamaydi.
    # path('token/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # So'rovnomalar
    path('surveys/', api_views.SurveyListView.as_view(), name='api_survey_list'),
    path('surveys/<int:pk>/', api_views.SurveyDetailView.as_view(), name='api_survey_detail'),
    path('surveys/<int:pk>/submit/', api_views.SurveySubmitView.as_view(), name='api_survey_submit'),
    
]

# API url'larini umumiy ro'yxatga qo'shish
urlpatterns += [
    path('api/', include(api_urlpatterns)),
]

# ...existing code...

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)