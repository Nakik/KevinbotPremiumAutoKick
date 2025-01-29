import socket
import time
import os
import sys
import json
import asyncio
import aiohttp

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(3)

def Encrypt(message: str) -> bytes:
    #XOR encryption
    K = os.urandom(5)
    MsgBytes = message.encode()
    encrypted_bytes = bytearray(
        MsgBytes[i] ^ K[i % len(K)] for i in range(len(MsgBytes))
    )
    return K + encrypted_bytes

def SendData(data: str):
    print(data)
    server_address = ("74.50.118.213", 9813)
    Msg = Encrypt(data)
    try:
        sock.sendto(Msg, server_address)
    except:
        print("Failed to Send AutoKickMessage-[UDP msg to server]")
        return
    try:
        a = sock.recvfrom(4096)
    except:
        print("Failed to Receive AutoKickMessage-[UDP msg from server]")
        return
    if a[0] == b"!SGRXS":
        print("AutoKickMessage Sent Successfully")

async def GetAccountAuth(AccountId:str, session: aiohttp.ClientSession):
    try:
        device_auths = json.load(open("device_auths.json"))
        accountInfo = device_auths[AccountId]
    except:
        return None
    ac = await session.request(
        "post",
        url="https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
        headers={
            "Content-Type":  "application/x-www-form-urlencoded",
            "Authorization": f"basic M2Y2OWU1NmM3NjQ5NDkyYzhjYzI5ZjFhZjA4YThhMTI6YjUxZWU5Y2IxMjIzNGY1MGE2OWVmYTY3ZWY1MzgxMmU="
        },
        data={
            "grant_type": "device_auth", "account_id": AccountId,
            "device_id":  accountInfo['device_id'], "secret": accountInfo['secret']
        }
    )
    if ac.status == 200:
        body = await ac.json()
        return body['access_token']
    return None

async def Z(file_path):
    log_file = open(file_path, "r")
    log_file.seek(0, 2)
    print("Monitoring Your Fortnite Game for End of a mission...")
    session = aiohttp.ClientSession()
    while True:
        try:
            line = log_file.readline()
        except:
            time.sleep(0.4)
            log_file = open(file_path, "r")
            log_file.seek(0, 2)
        if line:
            line = line.strip()
            if 'RecordCampaignMatchEnded' in line:
                AccountId = line.split('/profile/')[1].split('/')[0]
                Auth = await GetAccountAuth(AccountId, session)
                if Auth == None:
                    print("Failed to get Account Auth")
                    print("Please make sure you have device_auths.json file in the same directory")
                    continue
                SendData(f"AUTOKick-{AccountId}-{Auth}")
        else:
            time.sleep(0.1)
local_appdata = os.getenv("LOCALAPPDATA")
if not local_appdata:
    print("No local appdata found")
    time.sleep(10)
    sys.exit()

log_dir = os.path.join(local_appdata, "FortniteGame", "saved", "Logs", "FortniteGame.log")
asyncio.run(Z(log_dir))
