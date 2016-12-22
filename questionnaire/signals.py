from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FormData, EnrolledClients


@receiver(post_save, sender=FormData)
def enroll_client(sender, **kwargs):
    created = kwargs['created']
    instance = kwargs['instance']
    form_name = instance.form.name
    clinic = instance.data['clinic']
    if created and form_name == "Labor and Delivery Register" and instance.data['clinic'] != 'OTHER':
        EnrolledClients.objects.create(
            uuid=instance.uuid,
            client_id=instance.client_id,
            name=instance.data['name'],
            phone=instance.data['phone'],
            phone_relative=instance.data['phone_relative'],
            delivery_date=datetime.strptime(instance.data['delivery_date'], "%m/%d/%Y %H:%M:%S").date()
        )
    elif form_name == "Labor and Delivery Register" and clinic != 'OTHER':
        EnrolledClients.objects.filter(uuid=instance.uuid).update(
            client_id=instance.client_id,
            name=instance.data['name'],
            phone=instance.data['phone'],
            phone_relative=instance.data['phone_relative'],
            delivery_date=datetime.strptime(instance.data['delivery_date'], "%m/%d/%Y %H:%M:%S").date()
        )
