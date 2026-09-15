"""Customer profile linked one-to-one with the Django user."""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import TimeStampedModel


class CustomerProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    avatar = models.ImageField(upload_to="customers/", blank=True, null=True)

    class Meta:
        verbose_name = "Customer profile"

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_address(self):
        parts = [self.address, self.city, self.state, self.pincode]
        return ", ".join(p for p in parts if p)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    """Every user automatically gets a profile so templates never break."""
    if created:
        CustomerProfile.objects.get_or_create(user=instance)
    else:
        CustomerProfile.objects.get_or_create(user=instance)
