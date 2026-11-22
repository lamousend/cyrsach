from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        STAFF = "staff", "Сотрудник"
        ADMIN = "admin", "Администратор"

    role = models.CharField("роль", max_length=16, choices=Role.choices, default=Role.STUDENT)

    @property
    def is_room_admin(self) -> bool:
        return self.is_superuser or self.is_staff or self.role == self.Role.ADMIN