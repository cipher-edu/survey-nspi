# # auth_app/tests.py
# from django.test import TestCase, Client
# from django.urls import reverse
# from django.conf import settings
# from django.utils import timezone
# from unittest.mock import patch, MagicMock # Mocking uchun

# from .models import Student
# from .forms import LoginForm
# from .services.hemis_api_service import APIClientException # APIClientException ni import qilish

# # Testlar oldingi javobdagidek. Asosiy o'zgarishlar:
# # - _get_error_log_id mock qilinishi kerak bo'lgan joylarga e'tibor.
# # - settings.LOGIN_URL to'g'ri ishlatilishi.

# class AuthAppModelsTests(TestCase):

#     def test_student_model_str(self):
#         student = Student.objects.create(username="testuser", full_name_api="Test User Full")
#         self.assertEqual(str(student), "Test User Full")

#         student2 = Student.objects.create(username="anotheruser", first_name="Another", last_name="User")
#         self.assertEqual(str(student2), "User Another")

#         student3 = Student.objects.create(username="onlyusername")
#         self.assertEqual(str(student3), "onlyusername")

#     def test_student_birth_date_display(self):
#         test_timestamp = 946684800 # 1 yanvar 2000 yil 00:00:00 UTC
#         student = Student.objects.create(username="birthdatetest", birth_date_timestamp=test_timestamp)
        
#         # Test vaqt mintaqasini aniq belgilash yaxshiroq
#         with self.settings(TIME_ZONE='Asia/Tashkent'): # Yoki testingiz uchun mos vaqt mintaqasi
#             # from django.utils import timezone as django_timezone
#             # current_tz = django_timezone.get_current_timezone()
#             # expected_date = django_timezone.datetime.fromtimestamp(test_timestamp, tz=current_tz).strftime('%d-%m-%Y')
#             # Bu testda 'get_birth_date_display' UTC ga nisbatan formatlaydi, agar model shunday qilsa.
#             # Agar u lokal vaqtga o'girsa, test ham shuni kutishi kerak.
#             # Modeldagi get_birth_date_display timezone.get_current_timezone() ni ishlatadi.
#             self.assertEqual(student.get_birth_date_display, timezone.datetime.fromtimestamp(test_timestamp, tz=timezone.get_current_timezone()).strftime('%d-%m-%Y'))


#         student_no_bdate = Student.objects.create(username="nobirthdate")
#         self.assertIsNone(student_no_bdate.get_birth_date_display)


# class AuthAppFormsTests(TestCase):

#     def test_login_form_valid(self):
#         form_data = {'username': 'testuser', 'password': 'password123'}
#         form = LoginForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_login_form_missing_username(self):
#         form_data = {'password': 'password123'}
#         form = LoginForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('username', form.errors)

#     def test_login_form_missing_password(self):
#         form_data = {'username': 'testuser'}
#         form = LoginForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('password', form.errors)

# @patch('auth_app.views._get_error_log_id', return_value="mock_error_id") # Xatolik ID sini mock qilish
# class AuthAppViewsTests(TestCase):
#     def setUp(self):
#         self.client = Client()
#         # LOGIN_URL sozlamalardan olinadi, bu odatda URL nomi
#         self.login_url_name = settings.LOGIN_URL 
#         self.login_url = reverse(self.login_url_name)
#         self.dashboard_url = reverse('dashboard')
#         self.home_url = reverse('home')
#         self.student_user = Student.objects.create(username="testloginuser", id=1, student_id_number="S001")

#     def test_login_view_get(self, mock_get_error_id): # mock argumentini qabul qilish
#         response = self.client.get(self.login_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'auth_app/login.html')
#         self.assertIsInstance(response.context['form'], LoginForm)

#     def test_home_view_unauthenticated(self, mock_get_error_id):
#         response = self.client.get(self.home_url)
#         self.assertEqual(response.status_code, 200) 
#         self.assertTemplateUsed(response, 'auth_app/home.html') # Yoki login ga redirect

#     @patch('auth_app.views.HemisAPIClient') 
#     def test_login_view_post_success(self, MockHemisAPIClient, mock_get_error_id):
#         mock_api_instance = MockHemisAPIClient.return_value
#         mock_api_instance.login.return_value = ('fake_api_token', {'refresh_token_cookie_value': 'fake_refresh_cookie', 'expires_in': 3600})
#         mock_api_instance.get_account_me.return_value = {
#             'student_id_number': '353201107000',
#             'first_name': 'Test',
#             'second_name': 'User',
#             'full_name': 'Test User Full',
#             'hash': 'somehash',
#         }

#         form_data = {'username': '353201107000', 'password': '16172714o'}
#         response = self.client.post(self.login_url, data=form_data)

#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, self.dashboard_url, fetch_redirect_response=False) # fetch_redirect_response=False muhim
        
#         self.assertEqual(self.client.session.get('api_token'), 'fake_api_token')
#         self.assertTrue('student_db_id' in self.client.session)
        
#         student_exists = Student.objects.filter(username='S12345', first_name='Test').exists()
#         self.assertTrue(student_exists)

#     @patch('auth_app.views.HemisAPIClient')
#     def test_login_view_post_api_auth_failure(self, MockHemisAPIClient, mock_get_error_id):
#         mock_api_instance = MockHemisAPIClient.return_value
#         mock_api_instance.login.side_effect = APIClientException("Auth failed", 401, {"error": "bad_creds"}, "http://fake.api/login")

#         form_data = {'username': 'wronguser', 'password': 'wrongpassword'}
#         response = self.client.post(self.login_url, data=form_data)

#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'auth_app/login.html')
#         messages = list(response.context['messages'])
#         self.assertEqual(len(messages), 1)
#         self.assertIn("Login yoki parol xato.", str(messages[0]))
#         self.assertIn("(Xatolik ID: mock_error_id_APICLI)", str(messages[0])) # Xatolik ID si endi mock qilingan

#     def test_logout_view(self, mock_get_error_id):
#         session = self.client.session
#         session['api_token'] = 'test_token'
#         session['student_db_id'] = self.student_user.id
#         session.save()

#         logout_url = reverse('logout')
#         response = self.client.get(logout_url, follow=True) # follow=True xabarlarni olish uchun
        
#         # follow=True bo'lsa, oxirgi status_code 200 bo'ladi (login sahifasi)
#         self.assertEqual(response.status_code, 200) 
#         # Va redirectlar zanjirini tekshirish
#         self.assertRedirects(response, self.login_url, status_code=302, target_status_code=200)

#         self.assertNotIn('api_token', self.client.session)
#         self.assertNotIn('student_db_id', self.client.session)
        
#         messages = list(response.context['messages'])
#         self.assertEqual(len(messages), 1)
#         self.assertEqual(str(messages[0]), "Siz tizimdan muvaffaqiyatli chiqdingiz.")


#     def test_dashboard_view_unauthenticated(self, mock_get_error_id):
#         response = self.client.get(self.dashboard_url)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, f"{self.login_url}?next={self.dashboard_url}")

#     @patch('auth_app.views._handle_api_token_refresh', return_value=True)
#     def test_dashboard_view_authenticated(self, mock_token_refresh, mock_get_error_id):
#         session = self.client.session
#         session['api_token'] = 'valid_token'
#         session['student_db_id'] = self.student_user.id
#         session['api_token_expiry_timestamp'] = timezone.now().timestamp() + 3600
#         session.save()

#         response = self.client.get(self.dashboard_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'auth_app/dashboard.html')
#         self.assertEqual(response.context['student'], self.student_user)
#         mock_token_refresh.assert_called_once()

#     @patch('auth_app.views._handle_api_token_refresh', return_value=False)
#     def test_dashboard_view_token_refresh_fails(self, mock_token_refresh_fail, mock_get_error_id):
#         session = self.client.session
#         session['api_token'] = 'expiring_token'
#         session['student_db_id'] = self.student_user.id
#         session['hemis_refresh_cookie'] = 'some_refresh_cookie'
#         session['api_token_expiry_timestamp'] = timezone.now().timestamp() - 3600 
#         session.save()
        
#         response = self.client.get(self.dashboard_url)
#         self.assertEqual(response.status_code, 302) 
#         self.assertRedirects(response, self.login_url)
#         mock_token_refresh_fail.assert_called_once()

from auth_app.models import SurveyResponse, Answer
response = SurveyResponse.objects.filter(survey__id=2).last()
print(response.student)
answers = response.answers.all()
for answer in answers:
    print(f"Question: {answer.question.text}, Answer: {answer}")