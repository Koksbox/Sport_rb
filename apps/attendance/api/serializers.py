# apps/attendance/api/serializers.py
from rest_framework import serializers
from apps.attendance.models import AttendanceRecord, AbsenceReason
from apps.athletes.models import AthleteProfile

class AbsenceReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceReason
        fields = ['id', 'name']

class AttendanceRecordSerializer(serializers.ModelSerializer):
    athlete_name = serializers.CharField(source='athlete.user.get_full_name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    absence_reason = AbsenceReasonSerializer(read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'athlete', 'athlete_name', 'group', 'group_name',
            'date', 'status', 'comment'
        ]

class AttendanceMarkSerializer(serializers.ModelSerializer):
    absence_reason_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = AttendanceRecord
        fields = ['athlete', 'group', 'date', 'status', 'comment', 'absence_reason_id']

    def validate(self, attrs):
        # Проверка: тренер имеет доступ к группе
        request = self.context['request']
        group = attrs['group']
        coach = request.user.coach_profile
        if not group.coach_memberships.filter(
            coach=coach, status='active'
        ).exists():
            raise serializers.ValidationError("Нет доступа к этой группе.")
        return attrs

    def create(self, validated_data):
        reason_id = validated_data.pop('absence_reason_id', None)
        record = AttendanceRecord.objects.create(**validated_data)
        if reason_id and validated_data['status'] == 'absent':
            try:
                reason = AbsenceReason.objects.get(id=reason_id)
                record.absence_reason = reason
                record.save()
            except AbsenceReason.DoesNotExist:
                pass
        return record