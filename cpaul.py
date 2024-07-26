import requests
import sys


test_mission = "Order a Hawaiian Pizza with extra cheese and a side of garlic bread. Deliver it to 31 Pickens Lane, Toronto and pay with cash on delivery."
URL = 'NGROK URL'


def task_paul(mission, recipient):
    return requests.post(f'{URL}/task', data={
        'Mission': mission,
        'To': recipient
    })


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 test.py <recipient> [mission]')
        return

    recipient = sys.argv[1]
    mission = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else test_mission

    r = task_paul(mission, recipient)
    print(r.status_code)


if __name__ == '__main__':
    main()
