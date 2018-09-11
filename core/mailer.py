from django.core.mail import send_mail

send_mail(
	'Account created for ' + 'name',
	'An account has been created!',
	'mailer@creditability.com',
	['rem99@georgetown.edu'],
	fail_silently=True,
)