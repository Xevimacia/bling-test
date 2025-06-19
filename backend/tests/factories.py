import factory
from django.utils import timezone
from users.models import CustomUser
from cards.models import Card

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall('set_password', 'password')
    external_id = factory.Sequence(lambda n: f"ext{n}")

class CardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Card

    user = factory.SubFactory(UserFactory)
    color = "black"
    external_id = factory.Sequence(lambda n: f"card{n}")
    expiration_date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=365))
    status = "ordered" 