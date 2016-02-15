from django.db.models.signals import pre_save
from django.dispatch import receiver
from ..models import Institute


@receiver(pre_save, sender=Institute)
def call_back_save_institute(sender, **kwargs):
    pass
