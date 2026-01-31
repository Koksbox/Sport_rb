# Generated migration
from django.db import migrations


def set_default_registration_type(apps, schema_editor):
    """Устанавливаем registration_type='athlete' для существующих записей"""
    EventRegistration = apps.get_model('events', 'EventRegistration')
    EventRegistration.objects.filter(registration_type__isnull=True).update(registration_type='athlete')


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_create_event_invitation'),
    ]

    operations = [
        migrations.RunPython(set_default_registration_type, migrations.RunPython.noop),
    ]
