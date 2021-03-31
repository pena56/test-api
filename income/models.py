from django.db import models
from account.models import Account

# Create your models here.
class Income(models.Model):

  SOURCE_OPTIONS = (
    ('SALARY', 'SALARY'),
    ('BUSINESS', 'BUSINESS'),
    ('SIDE_HUSTLES', 'SIDE_HUSTLES'),
    ('OTHERS', 'OTHERS'),
  )

  source = models.CharField(max_length=80, choices=SOURCE_OPTIONS)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  description = models.TextField()
  owner = models.ForeignKey(to=Account, on_delete=models.CASCADE)
  date = models.DateField(null=False, blank=False)

  def __str__(self):
    return self.owner.username

  class Meta:
    ordering = ['-date']


