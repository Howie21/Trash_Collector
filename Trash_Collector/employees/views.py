from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.apps import apps
from datetime import date
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

    try:
        # This line will return the customer record of the logged-in user if one exists
        logged_in_employee = Employee.objects.get(user=logged_in_user)
        content_present = True
        today = date.today()
        customer_data = Customer.objects.filter(zip_code = logged_in_employee.zip_code)
        if len(list(customer_data)) == 0:
            content_present = False
        # customer_data_plain = list(Customer.objects.all())
        # customer_data = customer_data_plain.filter
        context = {
            'logged_in_employee': logged_in_employee,
            'today': today,
            'customer_data': customer_data,
            'content_present': content_present
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
