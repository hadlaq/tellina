from django.db import models
from django.utils import timezone

class NLRequest(models.Model):
    request_str = models.TextField()

    # used to display a list of query suggestions in the main page
    sub_time = models.DateTimeField(default=timezone.now)
    frequency = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.request_str


class Translation(models.Model):
    request = models.ForeignKey(NLRequest, on_delete=models.CASCADE)
    pred_cmd = models.TextField()
    score = models.FloatField()
    num_votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{}\n{}".format(self.request, self.pred_cmd)
