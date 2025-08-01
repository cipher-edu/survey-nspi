# auth_app/api_views.py

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Survey, Question, Choice, SurveyResponse, Answer, Student
from .serializers import SurveyListSerializer, SurveyDetailSerializer, SurveySubmitSerializer
from .permissions import CanRespondToSurvey
from .services.hemis_api_service import HemisAPIClient, APIClientException
from .utils import map_api_data_to_student_model_defaults

# Token olish uchun standart viewni moslashtirish
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Bu yerda HEMIS API orqali login logikasi bo'lishi kerak
        # Agar login muvaffaqiyatli bo'lsa, student uchun token generatsiya qilinadi
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username va password kiritilishi shart."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mavjud login_view dagi logikani shu yerga ko'chirish
        try:
            api_client = HemisAPIClient()
            api_token, _ = api_client.login(username, password)
            student_info_from_api = api_client.get_account_me(api_token_override=api_token)
            
            with transaction.atomic():
                student_defaults = map_api_data_to_student_model_defaults(student_info_from_api, username)
                student, _ = Student.objects.update_or_create(username=username, defaults=student_defaults)
            
            # Agar HEMIS login muvaffaqiyatli bo'lsa, biz o'zimizning JWT tokenimizni beramiz
            # Bu yerda biz Student modelini User sifatida ishlatishimiz kerak.
            # Buni amalga oshirish uchun Student modelini Django User modelidan meros olish yoki
            # Studentga bog'liq User yaratish kerak. Eng osoni - tokenga student ID ni qo'shish.
            refresh = self.get_serializer().get_token(student) # Bu yerda 'student' User obyekti bo'lishi kerak.
            # Hozircha Studentni User sifatida ishlatish uchun moslashtirish kerak.
            # Vaqtincha yechim:
            # Agar Student Django User bilan bog'liq bo'lsa, request.user.student
            # Agar yo'q bo'lsa, custom token yaratish kerak.
            # Keling, hozircha mavjud sessiya logikasiga o'xshash qoldiramiz va
            # bu yerni TODO deb belgilaymiz.
            
            # TODO: Student modelini Django User bilan to'g'ri bog'lash yoki
            #       custom JWT payload yaratish.
            # Hozirgi kodda bu qismi to'liq ishlamaydi, chunki Student - bu User emas.
            # To'g'ri yechim: Student yaratilganda unga mos Django User ham yaratish.
            
            return Response({"error": "API token logikasi hali to'liq sozlanmagan."}, status=status.HTTP_501_NOT_IMPLEMENTED)

        except APIClientException:
            return Response({"error": "Login yoki parol xato."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": f"Tizimda kutilmagan xatolik: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SurveyListView(generics.ListAPIView):
    """Talaba uchun mavjud bo'lgan barcha so'rovnomalar ro'yxati."""
    serializer_class = SurveyListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        return Survey.objects.filter(
            is_active=True, start_date__lte=now
        ).exclude(
            end_date__isnull=False, end_date__lt=now
        ).order_by('-start_date')

    def get_serializer_context(self):
        """Serializerga 'request' obyektini uzatish."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class SurveyDetailView(generics.RetrieveAPIView):
    """Bitta so'rovnomaning to'liq ma'lumotlari."""
    serializer_class = SurveyDetailSerializer
    permission_classes = [IsAuthenticated, CanRespondToSurvey]
    queryset = Survey.objects.filter(is_active=True).prefetch_related('questions__choices')

class SurveySubmitView(APIView):
    """So'rovnomaga javoblarni yuborish."""
    permission_classes = [IsAuthenticated, CanRespondToSurvey]

    def post(self, request, pk, *args, **kwargs):
        survey = get_object_or_404(Survey, pk=pk)
        self.check_object_permissions(request, survey) 

        serializer = SurveySubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data['answers']
        student = request.current_student

        try:
            with transaction.atomic():
                response = SurveyResponse.objects.create(survey=survey, student=student)

                for answer_data in validated_data:
                    question = Question.objects.get(id=answer_data['question_id'])
                    answer = Answer.objects.create(
                        survey_response=response,
                        question=question,
                        text_answer=answer_data.get('text_answer')
                    )
                    if question.question_type == 'single_choice' and answer_data.get('selected_choice_id'):
                        choice = Choice.objects.get(id=answer_data['selected_choice_id'])
                        answer.selected_choice = choice
                        answer.save()
                    elif question.question_type == 'multiple_choice' and answer_data.get('selected_choices_ids'):
                        choices = Choice.objects.filter(id__in=answer_data['selected_choices_ids'])
                        answer.selected_choices.set(choices)
            
            return Response({"message": "Javoblaringiz muvaffaqiyatli qabul qilindi."}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": f"Javoblarni saqlashda xatolik yuz berdi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)