import factory
from django.contrib.auth import get_user_model

from accounts.models import UserRole
from applications.models import Application, ApplicationStatus
from resumes.models import Resume
from vacancies.models import Vacancy, VacancyStatus

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    role = UserRole.JOB_SEEKER
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        if "password" not in kwargs:
            kwargs["password"] = "password123"
        return manager.create_user(*args, **kwargs)


class JobSeekerFactory(UserFactory):
    role = UserRole.JOB_SEEKER


class EmployerFactory(UserFactory):
    role = UserRole.EMPLOYER


class ResumeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Resume
        django_get_or_create = ("user",)

    user = factory.SubFactory(JobSeekerFactory)
    title = factory.Faker("job")
    summary = factory.Faker("paragraph")
    education = factory.LazyFunction(lambda: [{"institution": "University", "degree": "BSc"}])
    experience = factory.LazyFunction(lambda: [{"company": "Company", "title": "Developer", "years": 2}])


class VacancyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vacancy

    employer = factory.SubFactory(EmployerFactory)
    title = factory.Faker("job")
    description = factory.Faker("paragraph")
    salary_min = 1000
    salary_max = 2000
    status = VacancyStatus.OPEN


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

    resume = factory.SubFactory(ResumeFactory)
    vacancy = factory.SubFactory(VacancyFactory)
    status = ApplicationStatus.PENDING
