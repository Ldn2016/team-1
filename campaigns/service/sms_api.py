import os

from twilio.rest import TwilioRestClient

def send_sms(phone, sms_body):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    from_number = os.environ['TWILIO_PHONE_NUMBER']

    client = TwilioRestClient(account_sid, auth_token)
    client.messages.create(to=phone, from_=from_number, body=sms_body)
