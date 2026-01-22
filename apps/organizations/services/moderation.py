# apps/organizations/services/moderation.py
from django.utils import timezone
from apps.users.models import UserRole
from apps.notifications.models import Notification

def approve_organization(organization, moderator_user):
    """Одобрить организацию и назначить роль director"""
    from apps.organizations.models import Organization
    from apps.organizations.staff.director import Director

    if not organization.created_by:
        raise ValueError("Организация должна иметь created_by для назначения директора")

    organization.status = 'approved'
    organization.verified_at = timezone.now()
    organization.save(update_fields=['status', 'verified_at'])

    # Назначаем роль director
    user = organization.created_by
    UserRole.objects.get_or_create(user=user, role='director')

    # Создаём запись Director
    Director.objects.get_or_create(user=user, defaults={'organization': organization})

    # Уведомление
    Notification.objects.create(
        recipient=user,
        notification_type='org_approved',
        title='Ваша организация одобрена!',
        body=f'Организация "{organization.name}" теперь активна в каталоге.'
    )

    return organization