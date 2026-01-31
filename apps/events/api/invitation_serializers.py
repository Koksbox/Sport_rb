# apps/events/api/invitation_serializers.py
from rest_framework import serializers
from apps.events.models import EventInvitation, Event
from apps.athletes.models import AthleteProfile
from apps.coaches.models.coach_profile import CoachProfile

class EventInvitationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_date = serializers.DateTimeField(source='event.start_date', read_only=True)
    event_city = serializers.CharField(source='event.city.name', read_only=True)
    athlete_name = serializers.CharField(source='athlete.user.get_full_name', read_only=True, allow_null=True)
    coach_name = serializers.CharField(source='coach.user.get_full_name', read_only=True, allow_null=True)
    sent_by_name = serializers.CharField(source='sent_by.get_full_name', read_only=True)
    
    class Meta:
        model = EventInvitation
        fields = ['id', 'event', 'event_title', 'event_date', 'event_city', 
                  'invitation_type', 'athlete', 'athlete_name', 'coach', 'coach_name',
                  'sent_by', 'sent_by_name', 'status', 'message', 'expires_at',
                  'created_at', 'group_id', 'organization_id']
        read_only_fields = ['status', 'created_at']

class EventInvitationCreateSerializer(serializers.Serializer):
    """Сериализатор для создания приглашений"""
    event_id = serializers.IntegerField()
    invitation_type = serializers.ChoiceField(choices=['athlete', 'coach'], default='athlete')
    athlete_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
    coach_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
    group_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
    organization_id = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
