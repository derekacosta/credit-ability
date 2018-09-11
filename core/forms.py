import datetime

from django import forms
from django.contrib.auth.models import User

from core.models import *


class DateTypeInput(forms.DateInput):
    # used as a way to allow a date input type
    input_type = 'date'


class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = User
		fields = ('username', 'email', 'password')


class LoginForm(forms.Form):
	username = forms.CharField(required=True)
	password = forms.CharField(required=True, widget=forms.PasswordInput())


class AccountForm(forms.ModelForm):

	class Meta:
		model = Account
		fields = ('name', 'phone', 'address', 'city', 'gender', 'age', 'profile_photo', 'country')


class EmploymentForm(forms.ModelForm):

	class Meta:
		model = Employment
		fields = ('employer', 'phone', 'monthly_salary', 'start_date', 'end_date', 'currently_employed', 'paystub')
		widgets = {'start_date': DateTypeInput,
				   'end_date': DateTypeInput}


class IdentificationForm(forms.ModelForm):
    
    class Meta:
    	model = Identification
    	fields = ('name', 'file')


class FinancialInfoForm(forms.ModelForm):

	class Meta:
		model = FinancialInfo
		fields = ('monthly_income', 'housing_expense', 'time_in_europe', 'has_bank_account', 'num_months_debt',
				  'amount_in_bank', 'amount_cash', 'has_debts', 'amount_debts', 
				  'num_months_debt', 'ongoing_debt', 'reason_ongoing', 'missed_payments', 'loan_file')


class LeaseForm(forms.ModelForm):

	class Meta:
		model = Lease
		fields = ('amount', 'leaser_name', 'leaser_email', 'duration','months_left_in_current_job')

class CreateGroupForm(forms.ModelForm):
	
	class Meta:
		model = Group
		fields = ('code',)

class JoinGroupForm(forms.Form):
	code = forms.CharField()
