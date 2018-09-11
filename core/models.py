# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from .creditScore import creditScore

def getUpdatedCreditScore(user):
	#country, curIncMo, curHouseExp,workExp, bankAcc, bankBal, cashBal,arrLenMo,outDebt, outDebtAmt, outDebtTerm, paidDebt, misPay, misPayFreq
	account = user.account
	financials = FinancialInfo.objects.get(account=account)
	country = account.country
	curIncMo = financials.monthly_income
	curHouseExp = financials.housing_expense
	workExp = Employment.objects.filter(account=account).exists()
	bankAcc = financials.has_bank_account
	bankBal = financials.amount_in_bank
	cashBal = financials.amount_cash
	arrLenMo = financials.time_in_europe
	outDebt = financials.ongoing_debt
	outDebtAmt = financials.amount_debts
	outDebtTerm = financials.num_months_debt
	# the user has previously had debt and it is not ongoing, meaning it has been repaid
	paidDebt = financials.has_debts and (not financials.ongoing_debt) 
	misPay = (financials.missed_payments != 0)
	misPayFreq = financials.missed_payments

	credit_score = creditScore(curIncMo, curHouseExp, workExp, bankAcc, bankBal, cashBal,arrLenMo,outDebt, outDebtAmt, outDebtTerm, paidDebt, misPay, misPayFreq)

	return credit_score

COUNTRIES = (('Italy', 'Italy'),
			 ('France', 'France'),
			 ('Germany', 'Germany')
			)

REASONS = (('health', 'Health'),
			 ('lost_job', 'Lost Job'),
			 ('migration_issues', 'Migration Issues'),
			 ('other', 'Other')
			)

GENDERS = (('Male', 'Male'),
			('Female', 'Female'))

class Account(models.Model):
	# Link to the Django user account
	user = models.OneToOneField(User, on_delete=models.CASCADE)

	name = models.CharField(max_length=256)
	phone = models.CharField(max_length=100) # function to verify real phone number in form?
	address = models.CharField(max_length=256) # change to multiple lines, etc?
	city = models.CharField(max_length=256)
	gender = models.CharField(max_length=10, choices=GENDERS)
	age = models.IntegerField()
	country = models.CharField(max_length=256, choices=COUNTRIES)
	profile_photo = models.FileField(null=True, upload_to="profile_photos/")
	credit_score = models.IntegerField(blank=True, null=True)

	applied_for_lease = models.BooleanField(default=False)
	has_lease = models.BooleanField(default=False)

	share_key = models.CharField(max_length=16, blank=True, null=True)


class Employment(models.Model):
	account = models.ForeignKey(Account)
	employer = models.CharField(max_length=256)
	paystub = models.FileField(blank=True, null=True, upload_to="paystubs/")
	phone = models.CharField(max_length=100) # function to verify real phone number in form?
	start_date = models.DateField()
	end_date = models.DateField(blank=True, null=True)
	currently_employed = models.BooleanField(default=False, verbose_name="Currently Employed")
	monthly_salary = models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Monthly Salary")
	
	#make automatic updating of credit score
	@staticmethod
	def post_save(sender, **kwargs):
		instance = kwargs.get('instance')
		created = kwargs.get('created')
		if FinancialInfo.objects.filter(account=instance.account).exists():
			
			score = getUpdatedCreditScore(instance.account.user)
			instance.account.credit_score = score
			instance.account.save()
			print("Updating score:",score,"\nScore on account is:",instance.account.credit_score)


class Identification(models.Model):
	account = models.OneToOneField(Account)
	name = models.CharField(max_length=100)
	file = models.FileField(upload_to='id_documents/')


class FinancialInfo(models.Model):
	account = models.OneToOneField(Account)

	monthly_income = models.DecimalField(decimal_places=2, max_digits=12, default=0)
	housing_expense = models.DecimalField(decimal_places=2, max_digits=12, default=0)
	
	time_in_europe = models.IntegerField() # in months
	
	has_bank_account = models.BooleanField(default=False)
	amount_in_bank = models.DecimalField(decimal_places=2, max_digits=12, default=0)
	amount_cash = models.DecimalField(decimal_places=2, max_digits=12,blank=True, null=True,default=0)

	has_debts = models.BooleanField(default=False)
	amount_debts = models.DecimalField(decimal_places=2, max_digits=12, blank=True, default=0)
	num_months_debt = models.IntegerField(blank=True, null=True, default=0)
	ongoing_debt = models.BooleanField(default=False)
	reason_ongoing = models.CharField(max_length=256, choices=REASONS, blank=True, null=True)

	# What more needs to go here?
	missed_payments = models.IntegerField(blank=True, null=True, default=0)

	loan_file = models.FileField(upload_to="loan_docs/", blank=True, null=True)

	#make automatic updating of credit score
	@staticmethod
	def post_save(sender, **kwargs):
		instance = kwargs.get('instance')
		created = kwargs.get('created')
		score = getUpdatedCreditScore(instance.account.user)
		instance.account.credit_score = score
		instance.account.save()
		print("Updating score:",score,"\nScore on account is:",instance.account.credit_score)


class Group(models.Model):
	code = models.CharField(max_length=256)


class Lease(models.Model):
	account = models.OneToOneField(Account)

	amount = models.DecimalField(decimal_places=2, max_digits=12, default=0)
	leaser_name = models.CharField(max_length=256)
	leaser_email = models.CharField(max_length=256)

	guarantor_name = models.CharField(max_length=256, blank=True, null=True)
	gurantor_email = models.CharField(max_length=256, blank=True, null=True)

	duration = models.IntegerField(default=12) # in months
	payments_made = models.IntegerField(default=0, blank=True) # in months

	months_left_in_current_job = models.IntegerField(default=0)

	group = models.ForeignKey(Group, blank=True, null=True)

	approved = models.BooleanField(default=False)

	risk_profile_string = models.CharField(max_length=1024,null=True,blank=True)

signals.post_save.connect(Employment.post_save, sender=Employment)
signals.post_save.connect(FinancialInfo.post_save, sender=FinancialInfo)
