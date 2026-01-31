# apps/achievements/api/serializers.py
from rest_framework import serializers
from apps.achievements.models import Achievement, SportsRank, GtoResult, CoachAchievement
from apps.events.models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'start_date']

class AchievementSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()
    event_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Achievement
        fields = ['id', 'title', 'achievement_type', 'date', 'event', 'event_id', 'description', 'photo', 'photo_url', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None

    def validate_photo(self, value):
        if not value:
            raise serializers.ValidationError("Фото обязательно для добавления достижения")
        return value

    def create(self, validated_data):
        event_id = validated_data.pop('event_id', None)
        if event_id:
            try:
                validated_data['event'] = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                pass
        
        return super().create(validated_data)

class AchievementCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания достижения"""
    event_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Achievement
        fields = ['title', 'achievement_type', 'date', 'event_id', 'description', 'photo']
    
    def validate_photo(self, value):
        if not value:
            raise serializers.ValidationError("Фото обязательно для добавления достижения")
        return value

class SportsRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportsRank
        fields = ['id', 'rank', 'issued_by', 'issue_date', 'document_path']

class GtoResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GtoResult
        fields = ['id', 'level', 'badge', 'completion_date', 'protocol_number']

class CoachAchievementSerializer(serializers.ModelSerializer):
    """Сериализатор для достижений тренеров"""
    event = EventSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()
    event_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = CoachAchievement
        fields = ['id', 'title', 'achievement_type', 'date', 'event', 'event_id', 'description', 'photo', 'photo_url', 'issued_by', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None

    def validate_photo(self, value):
        if not value:
            raise serializers.ValidationError("Фото обязательно для добавления достижения")
        return value

    def create(self, validated_data):
        event_id = validated_data.pop('event_id', None)
        if event_id:
            try:
                validated_data['event'] = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                pass
        
        return super().create(validated_data)

class CoachAchievementCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания достижения тренера"""
    event_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = CoachAchievement
        fields = ['title', 'achievement_type', 'date', 'event_id', 'description', 'photo', 'issued_by']
    
    def validate_photo(self, value):
        if not value:
            raise serializers.ValidationError("Фото обязательно для добавления достижения")
        return value
