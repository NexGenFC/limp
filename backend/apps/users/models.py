from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models


class UserRole(models.TextChoices):
    FOUNDER = "FOUNDER", "Founder / Super Admin"
    MANAGEMENT = "MANAGEMENT", "Management"
    IN_HOUSE_ADVOCATE = "IN_HOUSE_ADVOCATE", "In-House Advocate"
    EXTERNAL_ADVOCATE = "EXTERNAL_ADVOCATE", "External Advocate"
    REVENUE_TEAM = "REVENUE_TEAM", "Revenue Team"
    SURVEYOR_INHOUSE = "SURVEYOR_INHOUSE", "Surveyor (In-House)"
    SURVEYOR_FREELANCE = "SURVEYOR_FREELANCE", "Surveyor (Freelance)"
    FIELD_STAFF = "FIELD_STAFF", "Field Staff"


class UserManager(DjangoUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True)
    role = models.CharField(
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.FIELD_STAFF,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
