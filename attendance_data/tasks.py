from celery import shared_task
from datetime import timedelta, datetime
from .models import AttenInfo, RemoteAttenInfo
from django.db.models import Q, Max
from collections import defaultdict
from send_notification.models import Registration

@shared_task(bind=True)
def fetch_attendance_data(self):
    print(f'Fetch attendance data function called at {datetime.now()}')

    #### Add data from remote server to local server
    student_id_to_courses_mapping = defaultdict(set)
    student_id_to_name_mapping = defaultdict(set)
    local_max_date = AttenInfo.objects.using('local_server').aggregate(max_date=Max('Date'))['max_date']
    print(f'local max date : {local_max_date}')
    if local_max_date:
        start_date = local_max_date + timedelta(1)
        end_date = datetime.now() + timedelta(-1)
        print(f'Fetching particular range data (From {start_date} to {end_date})...')
        curr_date = datetime.now() + timedelta(-1)
        data = RemoteAttenInfo.objects.using('remote_server').filter(Date__range=(start_date,end_date))
        data_to_insert = []
        for entry in data:  
            temp_model = AttenInfo(
                ID=entry.ID,
                Date=entry.Date,
                Time=entry.Time,
                StudentID=entry.StudentID,
                StudentName=entry.StudentName,
                CourseNo=entry.CourseNo
            )
            data_to_insert.append(temp_model)
            student_id_to_courses_mapping[entry.StudentID].add(entry.CourseNo)
            student_id_to_name_mapping[entry.StudentID].add(entry.StudentName)
        AttenInfo.objects.using('local_server').bulk_create(data_to_insert)

    else:
        print("Fetching all data...")
        curr_date = datetime.now()
        data = RemoteAttenInfo.objects.using('remote_server').filter(~Q(Date=f'{curr_date.year}-{curr_date.month}-{curr_date.day}'))
        data_to_insert = []
        for entry in data:  
            temp_model = AttenInfo(
                ID=entry.ID,
                Date=entry.Date,
                Time=entry.Time,
                StudentID=entry.StudentID,
                StudentName=entry.StudentName,
                CourseNo=entry.CourseNo
            )
            data_to_insert.append(temp_model)
            student_id_to_courses_mapping[entry.StudentID].add(entry.CourseNo)
            student_id_to_name_mapping[entry.StudentID].add(entry.StudentName)
        AttenInfo.objects.using('local_server').bulk_create(data_to_insert)
    #### End

    #### Update course registrations
    registrations = Registration.objects.using('local_server').all()
    updated_registrations = []
    for reg in registrations:
        student_id = reg.StudentID
        courses = (set(reg.Courses.split(';'))).union(student_id_to_courses_mapping[student_id])
        updated_courses = ';'.join(str(course) for course in courses)
        updated_registrations.append(
            {
                'StudentID' : student_id,
                'Courses' : updated_courses
            }
        )

    update_data_tuples = [(item['StudentID'], item['Courses']) for item in updated_registrations]
    students_to_update = []
    for StudentID, Courses in update_data_tuples:
        student = Registration.objects.using('local_server').get(StudentID=StudentID)
        student.Courses = Courses
        students_to_update.append(student)
    Registration.objects.using('local_server').bulk_update(students_to_update, ['Courses'])

    bulk_add_regs = []
    for StudentID in student_id_to_courses_mapping:
        student = Registration.objects.using('local_server').filter(StudentID=StudentID)
        if len(student):
            continue
        else :
            bulk_add_regs.append(
                Registration(
                    StudentID=StudentID,
                    Courses=';'.join(str(course) for course in student_id_to_courses_mapping[StudentID]),
                    Name=student_id_to_name_mapping[StudentID]
                )
            )
    Registration.objects.using('local_server').bulk_create(bulk_add_regs)
    #### End

    print(f'Fetch attendance data function finished at {datetime.now()}')
    return f'Done at {datetime.now()}'