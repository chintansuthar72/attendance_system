from celery import shared_task
from django.core.mail import send_mass_mail
from .models import Registration
from attendance_data.models import AttenInfo
from datetime import timedelta, datetime

@shared_task(bind=True)
def send_mails(self):

    date = datetime.now() + timedelta(-1)
    courses_temp = AttenInfo.objects.using('local_server').filter(Date=date).values('CourseNo').distinct()
    courses = [str(c['CourseNo']) for c in courses_temp if c['CourseNo'].lower()[:4] != 'exam']
    for course in courses:
        presents_temp = AttenInfo.objects.using('local_server').filter(Date=date).filter(CourseNo=course).values('StudentID')
        presents = [str(x['StudentID']) for x in presents_temp]
        alls_temp = Registration.objects.using('local_server').filter(Courses__icontains=course).values('StudentID')
        alls = [str(x['StudentID']) for x in alls_temp]
        absents = list(set(alls) - set(presents))

        content = []
        for absent in absents:
            message1 = (
                "You have missed the class of " + course + " on " + str(datetime.now().date() + timedelta(-1)),
                "",
                'settings.EMAIL_HOST_USER',
                [str(absent) + "@daiict.ac.in"],
            )
            content.append(message1)
        send_mass_mail(content,fail_silently=True)

    return "Done"