import requests


def task_paul(mission, recipient):
    r = requests.post('https://27ae-2001-8003-a0b9-c300-f1f8-3547-ca4b-b3c6.ngrok-free.app/task', data={
        'Mission': mission,
        'To': recipient
    })
    print(r.status_code)


m = "Order a Hawaiian Pizza with extra cheese and a side of garlic bread. Deliver it to 31 Pickens Lane, Toronto and pay with cash on delivery."
r = '+61417481991'
s = '+61400862607'

task_paul(m, s)
