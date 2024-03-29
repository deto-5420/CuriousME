from django.db import models
from accounts.models import Profile
from collectanea.globals import REPORT_STATUS
# Create your models here.

class ReportIssue(models.Model):
	user = models.ForeignKey(Profile, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	description = models.CharField(max_length=200)
	image = models.ImageField(upload_to='ReportIssue/', blank=True, null=True)
	status = models.CharField(max_length=50, choices=REPORT_STATUS, default=REPORT_STATUS[0])
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	def __str__(self):
		return self.title

