from django.db import models

# Create your models here.

class Deal(models.Model):
	title = models.CharField(max_length=200)
	post_date = models.DateTimeField()
	last_post_date = models.DateTimeField()
	source = models.CharField(max_length=50)
	post_id = models.IntegerField()
	
	def replyslope(self):
		lasttwo = self.history.all().order_by("-t")[:2]
		if len(lasttwo) >= 2:
			return lasttwo[0].replycount - lasttwo[1].replycount
		else:
			return 'New'

	def viewslope(self):
		lasttwo = self.history.all().order_by("-t")[:2]
		if self.history.count() >= 2:
			return lasttwo[0].viewcount - lasttwo[1].viewcount
		else:
			return 'New'
	
	def recent(self):
		return self.history.all().order_by("-t")[0]

	
class DealStatus(models.Model):
	replycount = models.IntegerField()
	viewcount = models.IntegerField()
	rating = models.IntegerField()
	t = models.DateTimeField()
	deal = models.ForeignKey(Deal, related_name='history')
	
class IgnoreList(models.Model):
	deal = models.ForeignKey(Deal, related_name='ignore')