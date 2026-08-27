from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    REQUIRED_FIELDS = ['age']

    age = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                15,
                message="L'utilisateur doit avoir au moins 15 ans.",
            )
        ]
    )
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
