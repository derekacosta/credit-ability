# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
import string
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import UpdateView
from .creditScore import creditScore
from django.core.mail import send_mail

from .defaultModel import applicant,individualDefaultRatio
from core.forms import *
from core.models import *

import json

@login_required(login_url='/login/')
def index(request):

	context = {'user': request.user,
			   'credit_score': request.user.account.credit_score}
	
	return render(request, 'core/index.html', context)


def register(request):

	user_form = UserForm()
	context = {'user_form': user_form}

	if request.method == 'POST':
		form = UserForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(username=form.cleaned_data['username'],
											email=form.cleaned_data['email'],
											password=form.cleaned_data['password'])
			messages.add_message(request, messages.SUCCESS, 'Account created.')
			return redirect('login')
		else:
			messages.add_message(request, messages.ERROR, 'Invalid form.')

	return render(request, 'core/register.html', context)


def login(request):
	
	login_form = LoginForm()
	context = {'login_form': login_form}

	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			#user = authenticate(username=form.cleaned_data.get('username'), 
			#					password=form.cleaned_data.get('password'))
			user = authenticate(username=request.POST.get('username'), 
									password=request.POST.get('password'))

			if user is not None:
				auth_login(request, user)
				if not Account.objects.filter(user=request.user).exists():
					return redirect('account-setup')
				else:
					return redirect('/')
			else:
				messages.add_message(request, messages.ERROR, 'Invalid login credentials.')
				return redirect('/login/')
		else:
			print(form.errors)
			messages.add_message(request, messages.ERROR, 'Invalid form')
			return redirect('/login/')

	return render(request, 'core/login.html', context)


@login_required(login_url='login')
def account_setup(request):

	account_form = AccountForm()
	context = {'account_form': account_form}

	if request.method == 'POST':
		form = AccountForm(request.POST, request.FILES)
		if form.is_valid():
			account = form.save(commit=False)
			account.user = request.user
			account.save()
			return redirect('history')
		else:
			print(form.errors)
			messages.add_message(request, messages.ERROR, 'Invalid form')			

	return render(request, 'core/account-setup.html', context)


@login_required(login_url='login')
def history(request):

	employment_form = EmploymentForm()
	prev_employment = Employment.objects.filter(account=request.user.account)
	file_form = IdentificationForm()
	# prefill if it already exists, and dont create a new one
	fin_info_form = FinancialInfoForm()

	context = {'employment_form': employment_form,
			   'employment': prev_employment,
			   'file_form': file_form,
			   'user': request.user,
			   'fin_info_form': fin_info_form}

	if request.method == 'POST':
		action = request.POST.get('action')
		print(action)
		if action == 'add_employment':
			form = EmploymentForm(request.POST)
			if form.is_valid():
				employment = form.save(commit=False)
				employment.account = request.user.account
				employment.save()
				messages.add_message(request, messages.SUCCESS, 'Employment Added')
			else:
				print(form.errors)
				messages.add_message(request, messages.ERROR, 'Invalid form')
		elif action == 'add_id':
			form = IdentificationForm(request.POST, request.FILES)
			if form.is_valid() and not Identification.objects.filter(account=request.user.account).exists():
				identification = form.save(commit=False)
				identification.account = request.user.account
				identification.save()
				messages.add_message(request, messages.SUCCESS, 'ID Added')
			else:
				print(request.user.account.id)
		elif action == 'fin_info':
			form = FinancialInfoForm(request.POST)
			if form.is_valid():
				fin_info = form.save(commit=False)
				fin_info.account = request.user.account
				fin_info.save()
				messages.add_message(request, messages.SUCCESS, 'Information saved.')
				credit_score = getUpdatedCreditScore(request.user)
				print(credit_score)
				request.user.account.credit_score = credit_score
				request.user.account.save()
			else:
				print(form.errors)

	return render(request, 'core/history.html', context)


@login_required(login_url='login')
def profile(request):

	profile = request.user.account
	
	if request.method == 'POST':
		action = request.POST.get('action')
		if action == 'share':
			if profile.share_key is None:
				profile.share_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
				print(profile.share_key)
				profile.save()
				# send email to leaser
			email = request.POST.get('email')
			print(email)
			send_mail(
				'Credit/Ability Score for ' + str(profile.name),
				'View the creditability score for ' + str(profile.name) + ' here: localhost:8000/viewinfo/' + profile.share_key,
				'mailer@creditability.com',
				[email],
				fail_silently=False,
			)
			messages.add_message(request, messages.SUCCESS, 'Message Sent!')
		elif action == 'reset':
			profile.share_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
			print(profile.share_key)
			profile.save()

	context = {'profile': profile}
	return render(request, 'core/profile.html', context)


class EditPersonalInfoView(UpdateView):
    model = Account
    form_class = AccountForm
    template_name = "core/edit-profile.html"

    def get_object(self, *args, **kwargs):
        user = self.request.user

        return user.account

    def get_success_url(self, *args, **kwargs):
        return reverse('profile')



@login_required(login_url='login')
def financials(request):

	#check if a financial profile exists for this user--page load will fail without one
	if not FinancialInfo.objects.filter(account=request.user.account).exists():
		return redirect('/history/')
	else:
		#otherwise...
		employment_form = EmploymentForm()
		financials = FinancialInfo.objects.get(account=request.user.account)
		account = request.user.account
		context = {'account': account,
				   'financials': financials,
				   'employment_form': employment_form}


		if request.method == 'POST':
			action = request.POST.get('action')
			print(action)
			if action == 'add_employment':
				form = EmploymentForm(request.POST)
				if form.is_valid():
					employment = form.save(commit=False)
					employment.account = request.user.account
					employment.save()
					messages.add_message(request, messages.SUCCESS, 'Employment Added')
				else:
					print(form.errors)
					messages.add_message(request, messages.ERROR, 'Invalid form')
			elif action == 'delete_employment':
				pk = request.POST.get('pk')
				employment = Employment.objects.get(pk=pk)
				employment.delete()


		return render(request, 'core/financials.html', context)


class EditFinancialInfoView(UpdateView):
    model = FinancialInfo
    form_class = FinancialInfoForm
    template_name = "core/edit-financials.html"

    def get_object(self, *args, **kwargs):
        user = self.request.user
        financials = FinancialInfo.objects.get(account=user.account)

        return financials

    def get_success_url(self, *args, **kwargs):
        return reverse('financials')


@login_required(login_url='login')
def faq(request):
	context = {}
	return render(request, 'core/faq.html', context)


@login_required(login_url='login')
def lease_apply(request):
	lease_form = LeaseForm()

	context = {'lease_form': lease_form,
			   'account': request.user.account}
	if request.method == 'POST':
		action = request.POST.get('action')
		if action == 'lease-app':
			form = LeaseForm(request.POST)
			if form.is_valid():
				lease = form.save(commit=False)
				lease.account = request.user.account
				#lease.save() not yet!
				messages.add_message(request, messages.SUCCESS, 'Application submitted!')
				request.user.account.applied_for_lease = True
				request.user.account.save()

				#perform a risk profile calculation using Yanchen's tool
				print("Leaser risk profile calculation:")
				acct = request.user.account

				empInfo = Employment.objects.filter(account = acct)
				employed=False
				for emp in empInfo:
					if emp.currently_employed:
						employed = True
				finInfo = FinancialInfo.objects.get(account = acct)
				bankBal = finInfo.amount_in_bank
				income = finInfo.monthly_income
				#secondary check
				if not employed:
					income = 0
				remainTerm = lease.months_left_in_current_job

				a = applicant(employed,income,bankBal,remainTerm,income)
				res = individualDefaultRatio(a,lease.amount,lease.duration)
				print(res)

				#save the risk profile data to this lease and save the lease
				lease.risk_profile_string = json.dumps(res)
				lease.save()

				return redirect('index')


	return render(request, 'core/lease-apply.html', context)


@login_required(login_url='login')
def join_group(request):
	join_form = JoinGroupForm()
	create_form = CreateGroupForm()

	if request.method == 'POST':
		action = request.POST.get('action')
		if action == 'join':
			form = JoinGroupForm(request.POST)
			if form.is_valid():
				my_code = form.cleaned_data['code']
				if Group.objects.filter(code=my_code).exists():
					group = Group.objects.get(code=my_code)
					lease = Lease.objects.get(account=request.user.account)
					if lease.group is None:
						lease.group = group
						lease.save()
					else:
						messages.add_message(request, messages.ERROR, "You are already in a group.")
				else:
					messages.add_message(request, messages.ERROR, 'Group does not exist.')
		elif action == 'create':
			group = CreateGroupForm(request.POST)
			group.save()
			messages.add_message(request, messages.ERROR, 'Group created!')


	context = {'account': request.user.account,
			   'join_form': join_form,
			   'create_form': create_form}
	return render(request, 'core/join-group.html', context)


@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    messages.add_message(request, messages.SUCCESS, 'Logged out successfully.')
    return redirect('/')


def leaser_view(request, share_key):
	print(share_key)
	access = False
	profile = None
	if Account.objects.filter(share_key=share_key).exists():
		access = True
		profile = Account.objects.get(share_key=share_key)
		print(profile)
	context = {'profile': profile,
			   'access': access}
	return render(request, 'core/leaser_view.html', context)
 

@user_passes_test(lambda u: u.is_superuser)
def superadmin(request):
	apps = []
	for l in Lease.objects.all(): 
		if not l.approved:
			print("Not approved!")
			print("Leaser Name:",l.leaser_name)
			print("Amount: ",l.amount)
			acct = l.account
			print("Acct is ",acct.credit_score)

			riskProfile = None
			if l.risk_profile_string is not None:
				riskProfile = json.loads(l.risk_profile_string)
				print("Risk profile is ",riskProfile)
				del riskProfile[len(riskProfile)-1]
			#convert risk profiles into percentages
			for i in range(len(riskProfile)):
				riskProfile[i] = 100.0*riskProfile[i]
			apps.append({'lease':l,
						'account':acct,
						'jobs':Employment.objects.filter(account=acct),
					  'risk_profile': riskProfile,
						})
	#done looping, construct final context
	context = {'applications': apps}

	return render(request, 'core/superadmin.html',context)
