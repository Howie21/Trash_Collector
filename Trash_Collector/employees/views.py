from django.db.models.fields.related import ForeignKey
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.apps import apps
from datetime import date
import calendar
from django.core.exceptions import ObjectDoesNotExist
from .models import Employee
from django.contrib.auth.decorators import login_required


# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.

@login_required
def index(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    Customer = apps.get_model('customers.Customer')
    logged_in_user = request.user
    weekdays = list(calendar.day_name)

    try:
        # This line will return the customer record of the logged-in user if one exists
        logged_in_employee = Employee.objects.get(user=logged_in_user)
        content_present = True
        today = date.today()
        weekday = weekdays[date.today().weekday()]
        customer_data = Customer.objects.filter(zip_code=logged_in_employee.zip_code)
        customer_data = customer_data.exclude(suspend_start__lt=today, suspend_end__gte=today) 
        if len(list(customer_data)) == 0:
            content_present = False
        context = {
            'logged_in_employee': logged_in_employee,
            'today': today,
            'customer_data': customer_data,
            'content_present': content_present,
            'weekday': weekday,
        }
        return render(request, 'employees/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:create'))

@login_required
def create(request):
    logged_in_user = request.user 
    if request.method == 'POST':
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip_code')
        new_employee = Employee(name=name_from_form, user=logged_in_user, zip_code=zip_from_form)
        new_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        return render(request, 'employees/create.html')

@login_required
def edit_profile(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        zip_from_form = request.POST.get('zip_code')
        logged_in_employee.name = name_from_form
        logged_in_employee.zip_code = zip_from_form
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'logged_in_employee': logged_in_employee
        }
        return render(request, 'employees/edit_profile.html', context)        

@login_required
def confirm(request, customer_id):
    Customer = apps.get_model('customers.Customer')
    customer_data = Customer.objects.get(pk= customer_id)
    customer_data.date_of_last_pickup = date.today()
    customer_data.balance = (customer_data.balance + 20)
    customer_data.one_time_pickup = None
    customer_data.save()
    return HttpResponseRedirect(reverse('employees:index'))
    if request.method == "GET":
        return render(request, 'employees:index')
 
@login_required
def filter(request):
    Customer = apps.get_model('customers.Customer')
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    customer_data = Customer.objects.filter(zip_code=logged_in_employee.zip_code)
    weekdays = list(calendar.day_name)
    weekday = weekdays[date.today().weekday()]
    if request.method == 'POST':
        weekday = request.POST.get('weekday')
        context = {
            'customer_data': customer_data,
            'weekday': weekday
        }
        return render(request, 'employees/filter.html', context)
    else:    
        context = {
            'customer_data': customer_data,
            'weekday': weekday
        }
    return render(request, 'employees/filter.html', context)


