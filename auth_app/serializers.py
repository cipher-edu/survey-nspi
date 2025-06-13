# auth_app/serializers.py

from rest_framework import serializers
from .models import Survey, Question, Choice, Student, SurveyResponse


class ChoiceWithCountSerializer(serializers.ModelSerializer):
    """
    Har bir javob varianti va unga necha kishi ovoz berganini ko'rsatadi.
    """
    count = serializers.IntegerField() # Bu qiymat view'da annotate orqali qo'shiladi

    class Meta:
        model = Choice
        fields = ['id', 'text', 'count']

class QuestionStatisticsSerializer(serializers.ModelSerializer):
    """
    Bitta savol va uning statistikasi (javob variantlari va ularning soni).
    """
    choices_stats = ChoiceWithCountSerializer(many=True, read_only=True)
    # Matnli javoblarni alohida qaytarish mumkin (agar kerak bo'lsa)
    text_answers = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        required=False
    )

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'choices_stats', 'text_answers']

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'is_required', 'choices']

class SurveyListSerializer(serializers.ModelSerializer):
    """So'rovnomalar ro'yxati uchun yengil serializer."""
    has_responded = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'is_anonymous', 'has_responded']

    def get_has_responded(self, obj):
        """
        Talabaning ushbu so'rovnomaga javob bergan yoki bermaganini tekshiradi.
        """
        student = self.context['request'].current_student
        if not student or obj.is_anonymous:
            return False # Agar talaba topilmasa yoki anonim bo'lsa, holat noma'lum
        return SurveyResponse.objects.filter(survey=obj, student=student).exists()

class SurveyDetailSerializer(SurveyListSerializer):
    """Bitta so'rovnomaning to'liq ma'lumotlari uchun serializer."""
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta(SurveyListSerializer.Meta):
        fields = SurveyListSerializer.Meta.fields + ['questions']


# Javoblarni qabul qilish uchun maxsus serializerlar
class AnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    # Frontend javob turiga qarab quyidagilardan birini yuboradi
    text_answer = serializers.CharField(required=False, allow_blank=True)
    selected_choice_id = serializers.IntegerField(required=False, allow_null=True)
    selected_choices_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_empty=True
    )

    def validate_question_id(self, value):
        if not Question.objects.filter(id=value).exists():
            raise serializers.ValidationError("Bunday IDga ega savol mavjud emas.")
        return value

class SurveySubmitSerializer(serializers.Serializer):
    answers = AnswerSubmitSerializer(many=True)