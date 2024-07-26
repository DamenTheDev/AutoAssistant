import openai
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse


# Twilio Settings
test_number = 'target_number'
from_number = 'from_number'
mission_prefix = "Hello, I am an AI in training. Please talk to me like you would a regular human. My name is Paul"
account_sid = 'SID'
auth_token = 'TOKEN'
client = Client(account_sid, auth_token)

# GPT Settings
openai.api_key = "APIKEY"
prompt = '''You are Paul, a polite AI who is currently calling someone. Your task is:
{}

Remember, this will be sent to a Text to Speech program, so make sure to keep your messages as short as possible and try not to repeat yourself unless asked.'''


def ask_gpt(messages):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150
    )
    resp = completion.choices[0].message.content
    print(resp)
    return resp


def get_chat(mission, user_first_message):
    return [{"role": "system", "content": prompt.format(mission)}, {"role": "user", "content": user_first_message}]


def call(mission, recipient, caller=None):
    if caller is None:
        caller = from_number

    resp = VoiceResponse()
    resp.say(mission, voice='Google.en-AU-Neural2-D', language='en-AU')
    resp.pause(length=1)

    call = client.calls.create(
        twiml=str(resp),
        to=recipient,
        from_=caller
    )
    return call.sid


#call(test_mission, test_number)

m = "Order a Hawaiian Pizza with extra cheese and a side of garlic bread. Deliver it to 31 Pickens Lane, Toronto and pay with cash on delivery."
first_message = "Hello, this is the oven, how may I help you?"
ms = get_chat(m, first_message)
ask_gpt(ms)
