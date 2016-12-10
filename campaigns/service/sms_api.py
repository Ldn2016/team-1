import os

from twilio.rest import TwilioRestClient

def send_sms(phone):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    from_number = os.environ['TWILIO_PHONE_NUMBER']

    sms_body = "Hello there!"

    client = TwilioRestClient(account_sid, auth_token)
    client.messages.create(to=phone, from_=from_number, body=sms_body)
