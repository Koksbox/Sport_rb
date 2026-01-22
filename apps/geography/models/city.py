# apps/geography/models/city.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .region import Region

SETTLEMENT_TYPE_CHOICES = [
    ('city', 'Город'),
    ('village', 'Село'),
    ('settlement', 'Деревня'),
    ('town', 'Поселок'),
]

class City(TimeStampedModel):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='cities')
    settlement_type = models.CharField(
        max_length=20, 
        choices=SETTLEMENT_TYPE_CHOICES, 
        default='city',
        help_text='Тип населенного пункта'
    )

    class Meta:
        db_table = 'geography_city'
        unique_together = ('name', 'region')

    def __str__(self):
        return f"{self.name}, {self.region.name}"
    
    def get_display_name(self):
        """Возвращает название с обозначением типа"""
        type_prefix = {
            'city': 'г.',
            'village': 'с.',
            'settlement': 'д.',
            'town': 'п.',
        }.get(self.settlement_type, '')
        return f"{type_prefix} {self.name}".strip() if type_prefix else self.name