from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import uuid


# Create your models here.
class User(AbstractUser):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    can_be_contacted = models.BooleanField(default=True)
    can_data_be_shared = models.BooleanField(default=False)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(15)],
        help_text="L'utilisateur doit avoir au moins 15 ans",
        default=15
    )

    def __str__(self):
        return self.username

    def clean(self):
        if self.age < 15:
            raise ValidationError('L\'utilisateur doit avoir au moins 15 ans')
