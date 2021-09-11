from decouple import config


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'testingtakenornot1@gmail.com'
EMAIL_HOST_PASSWORD = config('email_password')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'