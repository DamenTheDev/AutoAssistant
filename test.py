import requests


def task_paul(mission, recipient):
    r = requests.post('URL/task', data={
        'Mission': mission,
        'To': recipient
    })
    print(r.status_code)


m = "Order a Hawaiian Pizza with extra cheese and a side of garlic bread. Deliver it to 31 Pickens Lane, Toronto and pay with cash on delivery."
r = '...'
s = '...'

task_paul(m, s)
