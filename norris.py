import asyncio
import json
import websockets
import random
import requests

STATE = {'value':json.loads(requests.get(url="http://api.icndb.com/jokes/random/").text)['value']['joke']}

USERS = set()

def state_event():
	return json.dumps({'type':'state',**STATE})

def users_event():
	return json.dumps({'type':'users','count':	len(USERS)})

async def notify_state():
	if USERS:
		print('Button clicked, sending state')
		await asyncio.wait([user.send(state_event()) for user in USERS])

async def notify_users():
	if USERS:
		print('User connected, sending state')
		await asyncio.wait([user.send(users_event()) for user in USERS])
		await asyncio.wait([user.send(state_event()) for user in USERS])

async def register(websocket):
	USERS.add(websocket)
	await notify_users()

async def unregister(websocket):
	USERS.remove(websocket)
	await notify_users()

async def counter(websocket, path):
	await register(websocket)
	try:
		await websocket.send(state_event())
		async for message in websocket:
			data = json.loads(message)
			STATE['value'] = json.loads(requests.get(url="http://api.icndb.com/jokes/random/").text)['value']['joke']
			await notify_state()
	finally:
		await unregister(websocket)

asyncio.get_event_loop().run_until_complete(websockets.serve(counter, 'localhost',6789))
asyncio.get_event_loop().run_forever()