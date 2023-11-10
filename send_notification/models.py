from django.db import models

class Registration(models.Model):
    StudentID = models.CharField(max_length=50,primary_key=True)
    Courses = models.CharField(max_length=1000)
    Name = models.CharField(max_length=1000)

    class Meta:
        db_table = 'Registration'                                                                                                                                                        
        app_label = 'send_notification'