from django.http import HttpResponse
from django.shortcuts import render
from .models import AttenInfo, RemoteAttenInfo
from send_notification.models import Registration
from datetime import datetime
from django.db.models import Count
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


def home(request):
    return render(request, 'attendance_data/home.html')


def show_recent_data(request):
    data = AttenInfo.objects.using('local_server').all()[:20]
    context = {'data' : data}
    return render(request, 'attendance_data/show_recent_data.html', context=context)


def filter_page(request):
    courses = AttenInfo.objects.using('local_server').values('CourseNo').distinct()
    courses_list = [item['CourseNo'] for item in courses]
    return render(request, 'attendance_data/filter.html',{'courses':courses_list})


def day_wise_stud_per_course(request):
    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        course = request.POST['courses']
        start_date = datetime(day=int(str(start_date).split('-')[2]),year=int(str(start_date).split('-')[0]),month=int(str(start_date).split('-')[1]))
        end_date = datetime(day=int(str(end_date).split('-')[2]),year=int(str(end_date).split('-')[0]),month=int(str(end_date).split('-')[1]))
        
        all_ids_temp = Registration.objects.using('local_server').filter(Courses__icontains=course).values('StudentID').order_by('StudentID')
        all_ids = [str(x['StudentID']) for x in all_ids_temp]
        
        dates_temp = AttenInfo.objects.using('local_server').filter(Date__range=(start_date, end_date),CourseNo=str(course)).order_by('Date').values('Date').distinct()
        dates = [item['Date'] for item in dates_temp]

        data = []
        for id in all_ids:
            stu_data_temp = AttenInfo.objects.using('local_server').filter(Date__range=(start_date, end_date),CourseNo=str(course),StudentID=str(id)).order_by('Date').values('Date').distinct()
            stu_pre_dates = [item['Date'] for item in stu_data_temp]
            temp = []
            absent_dates = list(set(dates) - set(stu_pre_dates))
            for d in dates:
                if d in absent_dates: temp.append(0)
                else: temp.append(1)
            data.append({
                'StudentID' : id,
                'attendance' : temp,
                'ratio' : '-' if len(temp) == 0 else f'{sum(temp)}/{len(temp)}',
                'percentage' : '-' if len(temp) == 0 else round(sum(temp)*100/len(temp),2),
            })

        context = {
            'data' : data,
            'dates': dates,
            'selected_course' : course
        }

        return render(request, 'attendance_data/day_wise_stud_per_course.html', context=context)
    return HttpResponse("No data!")


def show_remote_recent_data(request):
    data = RemoteAttenInfo.objects.using('remote_server').order_by('-Date')[:20]
    context = {'data' : data}
    return render(request, 'attendance_data/show_recent_data.html', context=context)


def course_wise_percentage(request):
    selected_course = request.GET.get('course',None)
    courses = AttenInfo.objects.using('local_server').values('CourseNo').distinct()
    courses_list = [item['CourseNo'] for item in courses]

    if selected_course is None:
        context = {
            'courses' : courses_list,
            'selected_course' : selected_course,
        }
        return render(request, 'attendance_data/course_percentage.html', context=context)

    total_lectures_count = AttenInfo.objects.using('local_server').filter(CourseNo=selected_course).values('CourseNo').annotate(count=Count('Date',distinct=True))
    if total_lectures_count.exists():
        total_lectures_count = total_lectures_count[0]['count']
    else:
        total_lectures_count = 0

    id_wise_present_count =(AttenInfo.objects.using('local_server')
                            .filter(CourseNo=selected_course)
                            .values('StudentID')
                            .annotate(count=Count('Date',distinct=True))
                            .order_by('StudentID'))
    
    all_ids_temp = Registration.objects.using('local_server').filter(Courses__icontains=selected_course).values('StudentID')
    all_ids = [str(x['StudentID']) for x in all_ids_temp]

    ids_temp = []
    id_per = []
    for t in id_wise_present_count:
        ids_temp.append(t['StudentID'])
        id_per.append(
            {
                'StudentID': t['StudentID'],
                'count': t['count'],
                'percentage': 0 if total_lectures_count == 0 else round(((t['count'] * 100)/total_lectures_count),2)
            }
        )

    for id in set(all_ids) - set(ids_temp):
        id_per.append(
            {
                'StudentID': id,
                'count': 0,
                'percentage': 0
            }
        )

    id_per = sorted(id_per,key=lambda x: x['percentage'], reverse=True)

    context = {
        'courses' : courses_list,
        'selected_course' : selected_course,
        'total_lectures_count' : total_lectures_count,
        'id_wise_present_count' : id_per,
    }
    return render(request, 'attendance_data/course_percentage.html', context=context)


def course_per_less_x(request):

    req_per = float(request.GET.get('percentage',75.00))
    selected_course = request.GET.get('course',None)

    courses = AttenInfo.objects.using('local_server').values('CourseNo').distinct()
    courses_list = [item['CourseNo'] for item in courses]

    if selected_course is None or req_per is 0:
        context = {
            'courses' : courses_list,
            'selected_course' : selected_course,
            'selected_percentage' : req_per,
        }
        return render(request, 'attendance_data/course_per_less_x.html', context=context)

    total_lectures_count = AttenInfo.objects.using('local_server').filter(CourseNo=selected_course).values('CourseNo').annotate(count=Count('Date',distinct=True))
    if total_lectures_count.exists():
        total_lectures_count = total_lectures_count[0]['count']
    else:
        total_lectures_count = 0

    id_wise_present_count =(AttenInfo.objects.using('local_server')
                            .filter(CourseNo=selected_course)
                            .values('StudentID')
                            .annotate(count=Count('Date',distinct=True))
                            .order_by('StudentID'))
    
    all_ids_temp = Registration.objects.using('local_server').filter(Courses__icontains=selected_course).values('StudentID')
    all_ids = [str(x['StudentID']) for x in all_ids_temp]

    ids_temp = []
    id_per = []
    for t in id_wise_present_count:
        ids_temp.append(t['StudentID'])
        if round(((t['count'] * 100)/total_lectures_count),2) > req_per:
            continue
        id_per.append(
            {
                'StudentID': t['StudentID'],
                'count': t['count'],
                'percentage': 0 if total_lectures_count == 0 else round(((t['count'] * 100)/total_lectures_count),2)
            }
        )
    
    for id in set(all_ids) - set(ids_temp):
        id_per.append(
            {
                'StudentID': id,
                'count': 0,
                'percentage': 0
            }
        )

    id_per = sorted(id_per,key=lambda x: x['percentage'])
    context = {
        'courses' : courses_list,
        'selected_course' : selected_course,
        'selected_percentage' : req_per,
        'total_lectures_count' : total_lectures_count,
        'id_wise_present_count' : id_per,
    }
    return render(request, 'attendance_data/course_per_less_x.html', context=context)


def update_reg(request):

    if request.method == 'POST':
        selected_course = request.POST['courses']
        uploaded_file = request.FILES['excel_file']
        if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file)
            student_ids = df['student_id'].apply(str).tolist()
            existing_ids_temp = Registration.objects.using('local_server').filter(Courses__icontains=selected_course).values('StudentID')
            existing_ids = [str(x['StudentID']) for x in existing_ids_temp]

            to_be_updated = set(student_ids) - set(existing_ids)
            to_be_removed = set(existing_ids) - set(student_ids)

            students_to_update = []
            for id in to_be_removed:
                student = Registration.objects.using('local_server').get(StudentID=str(id).strip())
                current = str(student.Courses)
                updated_courses = current.replace(selected_course,'')
                updated_courses = updated_courses.replace(";;",';')
                if len(updated_courses) > 0 and updated_courses[0] == ';': updated_courses = updated_courses[1:]
                if len(updated_courses) > 0 and updated_courses[-1] == ';': updated_courses = updated_courses[:-1]
                student.Courses = updated_courses
                students_to_update.append(student)

            for id in to_be_updated:
                student = Registration.objects.using('local_server').get(StudentID=str(id).strip())
                student.Courses = str(student.Courses) + ";" + str(selected_course)
                students_to_update.append(student)
            
            Registration.objects.using('local_server').bulk_update(students_to_update, ['Courses'])

            context = {
                'success' : True
            }
            return render(request, 'attendance_data/course_update_finish.html', context=context)
        context = {
            'success' : False
        }
        return render(request, 'attendance_data/course_update_finish.html', context=context)
        
    else:
        courses = AttenInfo.objects.using('local_server').values('CourseNo').distinct()
        courses_list = [item['CourseNo'] for item in courses]

        context = {
            'courses' : courses_list
        }

        return render(request, 'attendance_data/update_reg.html', context=context)
    

def view_reg(request):

    courses = AttenInfo.objects.using('local_server').values('CourseNo').distinct()
    courses_list = [item['CourseNo'] for item in courses]
    selected_course = request.GET.get('course',None)
    if selected_course is None:
        return render(request, 'attendance_data/view_reg.html', context={'courses':courses_list, 'selected_course': selected_course ,'ids': []})
    existing_ids_temp = Registration.objects.using('local_server').filter(Courses__icontains=selected_course).values('StudentID','Name').order_by('StudentID')
    existing_ids = [(str(x['StudentID']),str(x['Name'])[2:-2]) for x in existing_ids_temp]
    return render(request, 'attendance_data/view_reg.html', context={'courses':courses_list,'selected_course': selected_course ,'ids': existing_ids})


def individual_student_performance(request):
    selected_student_id = request.GET.get('student_id',None)
    if selected_student_id is None:
        context = {
            'selected_student_id' : selected_student_id
        }
        return render(request, 'attendance_data/individual_student_performance.html', context)
    
    courses = Registration.objects.using('local_server').filter(StudentID=selected_student_id).values('Courses')
    
    if len(courses) > 0:
        courses_list = str(courses[0]['Courses']).split(';')
        data = []
        for course in courses_list:
            total_days = AttenInfo.objects.using('local_server').filter(CourseNo=course).values('Date').distinct().count()
            present_days = AttenInfo.objects.using('local_server').filter(CourseNo=course,StudentID=selected_student_id).values('Date').distinct().count()
            data.append({
                'CourseNo' : course,
                'total_lecture_count' : total_days,
                'attended_count' : present_days,
                'percentage' : 0 if total_days == 0 else round(present_days*100/total_days,2)
            })

        context = {
            'data' : data,
            'selected_student_id' : selected_student_id
        }
        return render(request, 'attendance_data/individual_student_performance.html', context)
    
    context = {
        'selected_student_id' : selected_student_id
    }
    return render(request, 'attendance_data/individual_student_performance.html', context)