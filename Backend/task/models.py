from django.db import models

class Task(models.Model):

    title = models.CharField(max_length=155, default='')
    description = models.CharField(max_length=510)
    status = models.CharField(max_length=10)
    due_date = models.DateField(null=True, blank=True)

class CustomList(models.Model):
    custom_list = models.CharField(max_length=200, null=True, default='')

    def save(self, *args, **kwargs):
        if not self.pk and CustomList.objects.exists():
            # if you'll not check for self.pk 
            # then error will also raised in update of exists model
            raise ValidationError('There is can be only one CustomList instance')
        return super(CustomList, self).save(*args, **kwargs)