from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random

from auth_app.models import (
    Student, Survey, SurveyFile, Question, Choice, SurveyResponse, Answer,
    ResponsiblePerson, MessageToResponsible, MessageAttachment
)

fake = Faker('uz_UZ')

class Command(BaseCommand):
    help = "Har bir model uchun 300 ta fake obyekt yaratadi va DB ga saqlaydi."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Fake data yaratish boshlandi..."))

        # 1. Students
        existing_usernames = set(Student.objects.values_list('username', flat=True))
        existing_ids = set(Student.objects.values_list('student_id_number', flat=True))
        existing_hashes = set(Student.objects.values_list('api_user_hash', flat=True))
        students = []
        attempts = 0
        while len(students) < 300 and attempts < 1000:
            username = fake.unique.bothify(text='stu####')
            student_id_number = fake.unique.bothify(text='ID####')
            api_user_hash = fake.unique.sha256()
            if username in existing_usernames or student_id_number in existing_ids or api_user_hash in existing_hashes:
                attempts += 1
                continue
            student = Student(
                username=username,
                student_id_number=student_id_number,
                api_user_hash=api_user_hash,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                patronymic=fake.first_name(),
                full_name_api=fake.name(),
                short_name_api=fake.first_name(),
                image_url=fake.image_url(),
                birth_date_timestamp=int(fake.date_of_birth().strftime('%s')),
                passport_pin=fake.bothify(text='A#######'),
                passport_number=fake.bothify(text='AB######'),
                email=fake.email(),
                phone=fake.phone_number(),
                gender_code=random.choice(['M', 'F']),
                gender_name=random.choice(['Erkak', 'Ayol']),
                university_name_api="Navoiy davlat universiteti",
                specialty_id_api=fake.bothify(text='SP####'),
                specialty_code_api=fake.bothify(text='SC###'),
                specialty_name_api=fake.job(),
                student_status_code=random.choice(['11', '12']),
                student_status_name=random.choice(['Faol', 'Akademik']),
                education_form_code=random.choice(['11', '12']),
                education_form_name=random.choice(['Kunduzgi', 'Sirtqi']),
                education_type_code=random.choice(['11', '12']),
                education_type_name=random.choice(['Bakalavr', 'Magistr']),
                payment_form_code=random.choice(['11', '12']),
                payment_form_name=random.choice(['Kontrakt', 'Grant']),
                group_id_api=random.randint(1, 20),
                group_name_api=fake.bothify(text='Guruh-##'),
                group_education_lang_code=random.choice(['uz', 'ru']),
                group_education_lang_name=random.choice(['O\'zbek', 'Rus']),
                faculty_id_api=random.randint(1, 10),
                faculty_name_api=fake.word(),
                faculty_code_api=fake.bothify(text='FC##'),
                education_lang_code=random.choice(['uz', 'ru']),
                education_lang_name=random.choice(['O\'zbek', 'Rus']),
                level_code=random.choice(['1', '2', '3', '4']),
                level_name=random.choice(['1-kurs', '2-kurs', '3-kurs', '4-kurs']),
                semester_id_api=random.randint(1, 8),
                semester_code_api=fake.bothify(text='S##'),
                semester_name_api=fake.word(),
                semester_is_current=random.choice([True, False]),
                semester_education_year_code=fake.year(),
                semester_education_year_name=fake.year(),
                semester_education_year_is_current=random.choice([True, False]),
                avg_gpa=str(round(random.uniform(2.0, 4.0), 2)),
                password_is_valid_api=True,
                address_api=fake.address(),
                country_code_api='UZ',
                country_name_api='O\'zbekiston',
                province_code_api=fake.bothify(text='P##'),
                province_name_api=fake.city(),
                district_code_api=fake.bothify(text='D##'),
                district_name_api=fake.city(),
                social_category_code=random.choice(['A', 'B']),
                social_category_name=random.choice(['Oddiy', 'Ijtimoiy']),
                accommodation_code=random.choice(['1', '2']),
                accommodation_name=random.choice(['Yotoqxona', 'Uy']),
                validate_url_api=fake.url(),
                last_login_api=timezone.now()
            )
            students.append(student)
            existing_usernames.add(username)
            existing_ids.add(student_id_number)
            existing_hashes.add(api_user_hash)
            attempts += 1
        Student.objects.bulk_create(students)
        self.stdout.write(self.style.SUCCESS(f"{len(students)} ta Student yaratildi."))

        # 2. ResponsiblePerson
        persons = []
        for i in range(20):
            person = ResponsiblePerson(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                patronymic=fake.first_name(),
                position=fake.job(),
                email=fake.email(),
                phone_number=fake.phone_number(),
                office_location=fake.address(),
                responsibilities_short=fake.sentence(),
                is_active=True
            )
            persons.append(person)
        ResponsiblePerson.objects.bulk_create(persons)
        self.stdout.write(self.style.SUCCESS("20 ta ResponsiblePerson yaratildi."))

        # 3. Survey
        surveys = []
        for i in range(350):
            survey = Survey(
                title=fake.sentence(nb_words=4),
                purpose=fake.sentence(),
                description=fake.text(),
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=random.randint(5, 350)),
                is_active=True,
                is_anonymous=random.choice([True, False]),
                created_by=None
            )
            surveys.append(survey)
        Survey.objects.bulk_create(surveys)
        self.stdout.write(self.style.SUCCESS("30 ta Survey yaratildi."))

        # 4. SurveyFile
        survey_files = []
        for survey in Survey.objects.all():
            for _ in range(random.randint(1, 3)):
                survey_files.append(SurveyFile(
                    survey=survey,
                    file=fake.file_name(extension='pdf'),
                    caption=fake.sentence()
                ))
        SurveyFile.objects.bulk_create(survey_files)
        self.stdout.write(self.style.SUCCESS("SurveyFile obyektlari yaratildi."))

        # 5. Question & Choice
        questions = []
        choices = []
        for survey in Survey.objects.all():
            for q_num in range(10):
                q_type = random.choice(['text', 'single_choice', 'multiple_choice'])
                question = Question(
                    survey=survey,
                    text=fake.sentence(),
                    question_type=q_type,
                    order=q_num,
                    is_required=random.choice([True, False])
                )
                questions.append(question)
        Question.objects.bulk_create(questions)
        self.stdout.write(self.style.SUCCESS("Savollar yaratildi."))

        for question in Question.objects.all():
            if question.question_type in ['single_choice', 'multiple_choice']:
                for c_num in range(5):
                    choices.append(Choice(
                        question=question,
                        text=fake.word()
                    ))
        Choice.objects.bulk_create(choices)
        self.stdout.write(self.style.SUCCESS("Variantlar yaratildi."))

        # 6. SurveyResponse & Answer
        responses = []
        answers = []
        students = list(Student.objects.all())
        questions = list(Question.objects.all())

        # Bazadagi mavjud (survey_id, student_id) juftliklarini to'plang
        existing_pairs = set(
            SurveyResponse.objects.values_list('survey_id', 'student_id')
        )
        # Sessionda generatsiya qilinayotgan juftliklarni ham tekshirish uchun
        new_pairs = set()

        for survey in Survey.objects.all():
            survey_students = random.sample(students, min(300, len(students)))
            for student in survey_students:
                pair = (survey.id, student.id if not survey.is_anonymous else None)
                # None student uchun unique_together ishlamaydi, faqat not anonymous uchun tekshiramiz
                if not survey.is_anonymous and (pair in existing_pairs or pair in new_pairs):
                    continue
                response = SurveyResponse(
                    survey=survey,
                    student=student if not survey.is_anonymous else None
                )
                responses.append(response)
                if not survey.is_anonymous:
                    new_pairs.add(pair)
        SurveyResponse.objects.bulk_create(responses)
        self.stdout.write(self.style.SUCCESS(f"{len(responses)} ta SurveyResponse obyektlari yaratildi."))

        responses = list(SurveyResponse.objects.all())
        # Savollar va variantlarni oldindan yuklab dictga joylang
        question_choices_map = {}
        for question in Question.objects.all():
            if question.question_type in ['single_choice', 'multiple_choice']:
                question_choices_map[question.id] = list(question.choices.all())

        answers = []
        m2m_answers = []  # ManyToMany uchun

        for response in responses:
            for question in response.survey.questions.all():
                answer = Answer(
                    survey_response=response,
                    question=question
                )
                if question.question_type == 'text':
                    answer.text_answer = fake.sentence()
                elif question.question_type == 'single_choice':
                    choices_q = question_choices_map.get(question.id, [])
                    if choices_q:
                        answer.selected_choice = random.choice(choices_q)
                elif question.question_type == 'multiple_choice':
                    choices_q = question_choices_map.get(question.id, [])
                    if choices_q:
                        # ManyToMany ni bulk_create'dan keyin alohida o'rnatamiz
                        m2m_answers.append((answer, random.sample(choices_q, random.randint(1, len(choices_q)))))
                answers.append(answer)
        Answer.objects.bulk_create([a for a in answers if not a.pk])
        self.stdout.write(self.style.SUCCESS("Answer obyektlari yaratildi."))

        # ManyToMany (selected_choices) ni alohida o'rnatish
        # Bulk_create'dan keyin Answer obyektlarini DBdan olish kerak
        answer_objs = Answer.objects.all()
        answer_map = {(a.survey_response_id, a.question_id): a for a in answer_objs}
        for answer, choices in m2m_answers:
            key = (answer.survey_response.survey_id, answer.question.id)
            real_answer = answer_map.get(key)
            if real_answer:
                real_answer.selected_choices.set([c.id for c in choices])

        self.stdout.write(self.style.SUCCESS("Answer.selected_choices (M2M) bog'lanishlari o'rnatildi."))

        # 7. MessageToResponsible & MessageAttachment
        messages_to_responsible = []
        for _ in range(300):
            msg = MessageToResponsible(
                student=random.choice(students),
                responsible_person=random.choice(ResponsiblePerson.objects.all()),
                subject=fake.sentence(),
                content=fake.text(),
                status=random.choice(['new', 'seen', 'answered', 'pending', 'closed']),
                response_content=fake.text(),
                responded_by=None,
                responded_at=timezone.now()
            )
            messages_to_responsible.append(msg)
        MessageToResponsible.objects.bulk_create(messages_to_responsible)
        self.stdout.write(self.style.SUCCESS("MessageToResponsible obyektlari yaratildi."))

        attachments = []
        for msg in MessageToResponsible.objects.all():
            for _ in range(random.randint(0, 2)):
                attachments.append(MessageAttachment(
                    message=msg,
                    file=fake.file_name(extension=random.choice(['pdf', 'jpg', 'png'])),
                    original_filename=fake.file_name(),
                ))
        MessageAttachment.objects.bulk_create(attachments)
        self.stdout.write(self.style.SUCCESS("MessageAttachment obyektlari yaratildi."))

        self.stdout.write(self.style.SUCCESS("Barcha fake ma'lumotlar yaratildi va DB ga yuklandi."))
