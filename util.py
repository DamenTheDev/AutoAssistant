from colorama import init
from termcolor import colored


init()


def gd(*args, **kwargs):
    print(colored('[+] ', 'green'), *args, **kwargs)


def bd(*args, **kwargs):
    print(colored('[-] ', 'red'), *args, **kwargs)


def nt(*args, **kwargs):
    print(colored('[*] ', 'blue'), *args, **kwargs)
