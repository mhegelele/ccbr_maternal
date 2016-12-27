from __future__ import unicode_literals

import uuid
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _
from django.core.urlresolvers import reverse

from autoslug import AutoSlugField


@python_2_unicode_compatible
class FormConfig(models.Model):
    name = models.CharField(_('Form Name'), max_length=64)
    slug = AutoSlugField(populate_from='name', unique=True)
    schema = JSONField(default={}, blank=True, null=True)
    options = JSONField(default={}, blank=True, null=True)
    double_verification = models.BooleanField(_('Double Verification?'), default=False)
    created = models.DateTimeField(_('Added'), auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('form-editor', kwargs={'slug': self.slug})

    def get_ids(self):
        return self.schema.get('unique')

    def get_data(self):
        data_forms = []
        for form in self.formdata_set.all():
            data_form = {
                'form_id': form.client_id,
                'uuid': form.uuid,
                'data': form.data,
                'created': form.created
            }
            if not data_form['form_id']:
                data_form['form_id'] = form.uuid
            data_forms.append(data_form)
        return data_forms


@python_2_unicode_compatible
class FormData(models.Model):
    uuid = models.UUIDField(_('UUID'), primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.CharField(_('ID'), max_length=30, editable=False, null=True)
    form = models.ForeignKey(FormConfig)
    data = JSONField(default={})
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)

    def __str__(self):
        return str(self.uuid)

    def get_absolute_url(self):
        return reverse('data-update', kwargs={'slug': self.form.slug, 'uuid': self.uuid})

    def save(self, *args, **kwargs):
        ids = []
        for key in self.form.schema.get('unique'):
            field_format = self.form.schema['properties'][key].get('format')
            if field_format == 'datetime' or field_format == 'date':
                ids.append(datetime.strptime(self.data[key], "%d/%m/%Y %H:%M:%S").date().strftime('%d%m%Y'))
            else:
                ids.append(self.data[key])
        self.client_id = '-'.join(ids)
        super(FormData, self).save(*args, **kwargs)


@python_2_unicode_compatible
class EnrolledClients(models.Model):
    uuid = models.UUIDField(_('UUID'), editable=False)
    client_id = models.CharField(max_length=30, editable=False, null=True)
    name = models.CharField(_('Client\'s Name'), max_length=96)
    phone = models.CharField(_('Phone No'), max_length=16)
    phone_relative = models.CharField(_('Relative\'s Phone No'), max_length=16)
    delivery_date = models.DateField(_('Delivery Date'))
    randomised = models.BooleanField(default=False)
    random_selection = models.BooleanField(_('Random Selection'), default=False)
    called = models.BooleanField(_('Contacted?'), default=False)
    available = models.BooleanField(_('Available?'), default=False)
    came_day7 = models.BooleanField(_('Came to clinic at 7th day after delivery?'), default=False)
    came_day28 = models.BooleanField(_('Came to clinic at 28th day after delivery?'), default=False)
    called_on_missed_visit2 = models.BooleanField(_('Called on missed visit 2?'), default=False)
    available_on_missed_visit2 = models.BooleanField(_('Available on missed visit 2 call?'), default=False)

    def __str__(self):
        return "{}: {}".format(self.name, self.phone)
