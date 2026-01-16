# apps/achievements/models/rank.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.athletes.models.profile import AthleteProfile

RANK_CHOICES = [
    ('junior', 'Юный спортсмен'),
    ('3rd_youth', 'III юношеский'),
    ('2nd_youth', 'II юношеский'),
    ('1st_youth', 'I юношеский'),
    ('3rd_adult', 'III взрослый'),
    ('2nd_adult', 'II взрослый'),
    ('1st_adult', 'I взрослый'),
    ('cms', 'КМС'),
    ('ms', 'Мастер спорта'),
    ('msr', 'МСМК'),
]

class SportsRank(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='ranks')
    rank = models.CharField(max_length=20, choices=RANK_CHOICES)
    issued_by = models.CharField(max_length=255)
    issue_date = models.DateField()
    document_path = models.CharField(max_length=500)

    class Meta:
        db_table = 'achievements_rank'