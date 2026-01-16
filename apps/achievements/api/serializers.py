# apps/achievements/api/serializers.py
from rest_framework import serializers
from apps.achievements.models import Achievement, SportsRank, GtoResult
from apps.events.models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'start_date']

class AchievementSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Achievement
        fields = ['id', 'title', 'achievement_type', 'date', 'event', 'description']

class SportsRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportsRank
        fields = ['id', 'rank', 'issued_by', 'issue_date', 'document_path']

class GtoResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GtoResult
        fields = ['id', 'level', 'badge', 'completion_date', 'protocol_number']