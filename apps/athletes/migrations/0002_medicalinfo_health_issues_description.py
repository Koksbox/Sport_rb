# Generated manually
from django.db import migrations
import apps.core.models.encryption


class Migration(migrations.Migration):

    dependencies = [
        ('athletes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalinfo',
            name='health_issues_description',
            field=apps.core.models.encryption.EncryptedTextField(blank=True, help_text='Описание проблем со здоровьем'),
        ),
    ]
