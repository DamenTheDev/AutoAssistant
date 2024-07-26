import openai


openai.api_key = "api-key"
INTRO = "Hello, I am an AI in training. Please be patient as it can take some time for me to respond. My name is Paul, with whom am I speaking?"
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


with open('prompt.txt', 'r') as f:
    prompt = f.read()


def generate_missions():
    comp = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[{"role": "system", "content": "You are to generate helpful content to train an AI. The AI will be used to call numbers to perform a certain objective like \"Order a large Hawaiian Pizza with extra cheese and a side of garlic bread and deliver it to 31 Pickens Lane, Toronto and pay with cash on delivery\" or \"Ask for Seb and prank him with the 'is your fridge running' joke, then immediately hang up\". You are to generate a list of objectives when asked"}, {"role": "user", "content": "Generate a list of 20 objectives, one per line with no numbers etc. and come up with a fictional person who would be answering the phone in this scenario including their name, employer and role in their company"}],
    )
    x = comp.choices[0].message.content.split('\n')
    while '' in x:
        x.remove('')
    for i in range(len(x)):
        x[i] = x[i].strip()
        if x[i][0] in ['-', '*', '"', "'", '•']:
            x[i] = x[i][1:].strip()
        if x[i][-1] in ['-', '*', '"', "'", '•']:
            x[i] = x[i][:-1].strip()
    return x


def evaluate_mission(mission):
    comp = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[{"role": "system", "content": "You are a human who is answering a phone call, you need to help the AI calling you complete its objective."},
                  {"role": "user", "content": INTRO}],
        max_tokens=150
    )
    result = comp.choices[0].message.content
    print(mission)
    print(result)
    #comp = openai.ChatCompletion.create(
    #    model="gpt-4-0613",
    #    messages=[{"role": "system", "content": prompt.replace("%MISSION%", mission)}, {"role": "assistant", "content": INTRO}],
    #    max_tokens=150
    #)


with open('missions.txt', 'r') as f:
    x = f.read().split('\n')
x = generate_missions()
print('Generated missions:')
print('\n'.join(x))
print()
print(x)
with open('missions.txt', 'w') as f:
    f.write('\n'.join(x))
for i in x:
    #evaluate_mission(i)
    break
