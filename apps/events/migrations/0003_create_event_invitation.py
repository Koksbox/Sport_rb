# Generated migration
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_add_registration_type_and_coach'),
        ('athletes', '0001_initial'),
        ('coaches', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EventInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invitation_type', models.CharField(choices=[('athlete', 'Спортсмен'), ('coach', 'Тренер')], default='athlete', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Ожидает ответа'), ('accepted', 'Принято'), ('declined', 'Отклонено'), ('expired', 'Истекло')], default='pending', max_length=20)),
                ('message', models.TextField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('group_id', models.IntegerField(blank=True, null=True)),
                ('organization_id', models.IntegerField(blank=True, null=True)),
                ('athlete', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_invitations', to='athletes.athleteprofile')),
                ('coach', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_invitations', to='coaches.coachprofile')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='events.event')),
                ('sent_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_event_invitations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'events_invitation',
            },
        ),
        migrations.AddIndex(
            model_name='eventinvitation',
            index=models.Index(fields=['status', 'invitation_type'], name='events_inv_status__idx'),
        ),
        migrations.AddIndex(
            model_name='eventinvitation',
            index=models.Index(fields=['athlete', 'status'], name='events_inv_athlete__idx'),
        ),
        migrations.AddIndex(
            model_name='eventinvitation',
            index=models.Index(fields=['coach', 'status'], name='events_inv_coach_s__idx'),
        ),
        migrations.AddField(
            model_name='eventregistration',
            name='invitation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registrations', to='events.eventinvitation'),
        ),
    ]
