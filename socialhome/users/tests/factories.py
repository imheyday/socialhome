import factory
from allauth.account.models import EmailAddress
from factory import fuzzy

from federation.entities import base

from socialhome.enums import Visibility


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: "user-{0}".format(n))
    email = factory.Sequence(lambda n: "user-{0}@example.com".format(n))
    password = factory.PostGenerationMethodCall("set_password", "password")

    class Meta:
        model = "users.User"

    @factory.post_generation
    def with_verified_email(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        EmailAddress.objects.create(
            user=self,
            email=self.email,
            verified=True,
        )


class PublicUserFactory(UserFactory):
    @classmethod
    def _generate(cls, create, attrs):
        user = super(UserFactory, cls)._generate(create, attrs)
        user.profile.visibility = Visibility.PUBLIC
        user.profile.save(update_fields=["visibility"])
        return user


class AdminUserFactory(UserFactory):
    is_superuser = True
    is_staff = True

    username = "admin"


class ProfileFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    email = factory.Faker("safe_email")
    handle = factory.SelfAttribute("email")
    guid = factory.Faker("uuid4")

    # Dummy strings as keys since generating these is expensive
    rsa_private_key = fuzzy.FuzzyText()
    rsa_public_key = fuzzy.FuzzyText()

    # Dummy image urls
    image_url_small = "https://127.0.0.1:8000/foo/small.png"
    image_url_medium = "https://127.0.0.1:8000/foo/medium.png"
    image_url_large = "/foo/large.png"

    class Meta:
        model = "users.Profile"


class PublicProfileFactory(ProfileFactory):
    visibility = Visibility.PUBLIC


class BaseProfileFactory(factory.Factory):
    class Meta:
        model = base.Profile

    handle = factory.Faker("safe_email")
    raw_content = factory.Faker("paragraphs", nb=3)
    email = factory.Faker("safe_email")
    gender = factory.Faker("job")
    location = "internet"
    nsfw = factory.Faker("pybool")
    public_key = factory.Faker("sha1")
    public = factory.Faker("pybool")
    guid = factory.Faker("uuid4")
    image_urls = {
        "small": factory.Faker("image_url", width=30, height=30).generate({}),
        "medium": factory.Faker("image_url", width=100, height=100).generate({}),
        "large": factory.Faker("image_url", width=300, height=300).generate({}),
    }
    tag_list = factory.Faker("words", nb=4)


class BaseShareFactory(factory.Factory):
    class Meta:
        model = base.Share

    guid = factory.Faker("uuid4")
    handle = factory.Faker("safe_email")
    target_guid = factory.Faker("sha1")
    target_handle = factory.Faker("safe_email")
    public = factory.Faker("pybool")
