from django.db import models

class AttenInfo(models.Model):
    ID = models.AutoField(primary_key=True)
    Date = models.DateField()
    Time = models.CharField(max_length=50)
    StudentID = models.CharField(max_length=50)
    StudentName = models.CharField(max_length=500)
    CourseNo = models.CharField(max_length=50)

    def __str__(self):
        return self.StudentName
    
    class Meta:
        db_table = 'AttenInfo'                                                                                                                                                        
        app_label = 'attendance_data'

class RemoteAttenInfo(models.Model):
    ID = models.AutoField(primary_key=True)
    Date = models.DateField()
    Time = models.CharField(max_length=50)
    StudentID = models.CharField(max_length=50)
    StudentName = models.CharField(max_length=500)
    CourseNo = models.CharField(max_length=50)

    def __str__(self):
        return self.StudentName
    
    class Meta:
        managed = False
        db_table = 'AttenInfo'                                                                                                                                                        
        app_label = 'attendance_data'