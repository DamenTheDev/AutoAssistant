import twilio
from twilio.twiml.voice_response import VoiceResponse
import websockets
from websockets.server import serve
import asyncio
from util import *


"""
This is a library for streaming audio to and from Twilio's Programmable Voice API.
"""


async def audio(websocket):
    async for message in websocket:
        print(message)


async def main():
    nt("Starting River server...")
    async with serve(audio, 'localhost', 8765):
        await asyncio.Future()


asyncio.run(main())
