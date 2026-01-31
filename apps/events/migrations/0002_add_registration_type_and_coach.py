# Generated migration
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
        ('coaches', '0001_initial'),
        ('athletes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventregistration',
            name='registration_type',
            field=models.CharField(choices=[('athlete', 'Спортсмен'), ('coach', 'Тренер')], default='athlete', max_length=20),
        ),
        migrations.AddField(
            model_name='eventregistration',
            name='coach',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_registrations', to='coaches.coachprofile'),
        ),
        migrations.AlterField(
            model_name='eventregistration',
            name='athlete',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_registrations', to='athletes.athleteprofile'),
        ),
        migrations.AlterUniqueTogether(
            name='eventregistration',
            unique_together={('event', 'athlete', 'registration_type'), ('event', 'coach', 'registration_type')},
        ),
        migrations.AddIndex(
            model_name='eventregistration',
            index=models.Index(fields=['status', 'registration_type'], name='events_reg_status__idx'),
        ),
    ]
