from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail

# Create your views here.

def send_notification(request):
    message = request.POST['message']
    email = request.POST['email']
    subject = request.POST['subject']
    student_id = request.POST['student_id']

    result = send_mail(
        subject=subject,
        message=message,
        from_email='settings.EMAIL_HOST_USER',
        recipient_list=[email],
        fail_silently=False
    )

    if result == 1 : 
        return HttpResponse(f'Email notification sent to id {student_id}.')
    
    return HttpResponse(f'Email notification sending error to id {student_id}.')
