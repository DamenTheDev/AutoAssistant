import openai
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import flask
import json
import requests


openai.api_key = "api-key"
default_caller = ""
with open('prompt.txt', 'r') as f:
    prompt = f.read()
account_sid = 'sid'
auth_token = 'token'
client = Client(account_sid, auth_token)
app = flask.Flask(__name__)
pauls = {}
SEND_INTRO = True

# Variables
INTRO = "Hello, I am an AI in training. Please be patient as it can take some time for me to respond. My name is Paul, with whom am I speaking?"
URL = 'URL'
WEBHOOK_URL = 'DISCORD WEBHOOK URL'
VOICE = 'Google.en-AU-Neural2-D'
LANGUAGE = 'en-AU'
MAX_TOKENS = 150
MODEL = "gpt-4-0613"
FUNCTIONS = [
    {
        "name": "hangup",
        "description": "Hangs up the call and gives the result of the call to the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "The result of the call."
                },
                "farewell": {
                    "type": "string",
                    "description": "The farewell message to say before hanging up."
                }
            },
            "required": ["result", "farewell"]
        },
    }
]


def hangup():
    resp = VoiceResponse()
    resp.hangup()
    return str(resp)


def send_to_discord(message, role):
    data = {
        "content": message,
        "embeds": None,
        "username": role.capitalize(),
        "attachments": []
    }
    requests.post(WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})


# Status Codes
HANGUP = 5
CONTINUE = 6


class Paul(object):
    def __init__(self, mission, recipient, caller=None):
        self.mission = mission
        self.recipient = recipient
        self.caller = caller if caller is not None else default_caller
        self.messages = [{"role": "system", "content": prompt.replace("%MISSION%", mission)}, {"role": "assistant", "content": INTRO}]
        self.new = True

    def call(self):
        global pauls
        if self.recipient in pauls:
            return
        send_to_discord(f"Calling `*{self.recipient[-3:]}` with the following objective:\n```{self.mission}```", "system")
        pauls[self.recipient] = self
        call = client.calls.create(
            url=f'{URL}/gather',
            record=True,
            machine_detection="Enable",
            to=self.recipient,
            from_=self.caller
        )
        return call.sid

    def query(self):
        print('[CALL] ->', self.recipient, 'TO GPT:')
        # self.print_messages()

        completion = openai.ChatCompletion.create(
            model=MODEL,
            messages=self.messages,
            max_tokens=150,
            functions=FUNCTIONS,
            function_call="auto"
        )
        #print(completion)
        resp = completion.choices[0].message

        #print(resp)

        # Check for functions
        if resp.get("function_call"):
            func_name = resp["function_call"]["name"]
            func_args = json.loads(resp["function_call"]["arguments"])
            print(f'[CALL] <- {self.recipient} FUNCTION {func_name}({func_args})')

            funcs = {
                "hangup": self.func_hangup
            }
            if func_name in funcs:
                return funcs[func_name](**func_args)

        if resp.get("content"):
            print('[CALL] <-', self.recipient, 'FROM GPT:', resp)
            self.messages.append({"role": "assistant", "content": resp["content"]})
            return resp["content"], CONTINUE

        print("[CALL] <-", self.recipient, "FROM GPT:", resp)
        return "I apologize, there was an error. Goodbye.", HANGUP

    def print_messages(self):
        for message in self.messages:
            print(message['role'], '->', message['content'])

    def func_hangup(self, result, farewell):
        send_to_discord(result, "system")
        return farewell, HANGUP

    def process(self, message=None, human=True):
        first = False
        if message is not None:
            print(f'[CALL] -> {self.recipient}:', message)
        elif self.new:
            self.new = False
            first = True
            if not human:
                message = "(Message bank)\n" + message if message is not None else "(Message bank)"
            print(f'[CALL] -> {self.recipient} BEGIN')
        else:
            print(f'[CALL] -> {self.recipient} NO MESSAGE')

        if not first:
            message = message if message is not None else "..."
            send_to_discord(message, "User")
            self.messages.append({"role": "user", "content": message})
            reply, code = self.query()
            resp = VoiceResponse()
            resp.say(reply, voice=VOICE, language=LANGUAGE)
            send_to_discord(reply, "Paul")
            if code == CONTINUE:
                resp.gather(input='speech', speech_timeout='auto', action=f'{URL}/gather', method='POST', profanity_filter=False, speech_model='experimental_utterances', action_on_empty_result=True)
            else:
                print(f'[CALL] -> {self.recipient} ENDED')
                send_to_discord(f"Call with `*{self.recipient[-3:]}` ended.", "system")
                del pauls[self.recipient]
            return str(resp)

        resp = VoiceResponse()
        if first and human and SEND_INTRO:
            resp.say(INTRO, voice=VOICE, language=LANGUAGE)
        resp.gather(input='speech', speech_timeout='auto', action=f'{URL}/gather', method='POST', profanity_filter=False, speech_model='experimental_utterances', action_on_empty_result=True)
        return str(resp)


def preprocess(content):
    return content.replace("YouTube", "you too")


@app.route('/gather', methods=['GET', 'POST'])
def gather():
    print(flask.request.form)
    try:
        call_status = flask.request.form['CallStatus']
        recipient = flask.request.form['To']
    except KeyError:
        print('Invalid request')
        return hangup()

    if call_status == 'completed':
        del pauls[recipient]
        print(f'[CALL] -> {recipient} ENDED')
        return hangup()
    elif call_status == 'in-progress' and recipient in pauls:
        paul = pauls[recipient]
        message = None
        if "SpeechResult" in flask.request.form:
            message = preprocess(flask.request.form['SpeechResult'])
        if "AnsweredBy" in flask.request.form:
            if flask.request.form['AnsweredBy'] not in ['human', 'unknown']:
                return paul.process(message, human=False)
        return paul.process(message)
    else:
        print('Unknown call status: {}'.format(call_status))
        return hangup()


@app.route('/task', methods=['POST'])
def task():
    # Get the destination number from the incoming POST request
    destination_number = flask.request.form['To']
    # Get the mission from the incoming POST request
    mission = flask.request.form['Mission']

    # Create a new Paul instance
    paul = Paul(mission, destination_number)
    # Call the recipient
    paul.call()
    return 'OK'


if __name__ == '__main__':
    send_to_discord("Paul is online!", "system")
    app.run(host='', port=8080)
