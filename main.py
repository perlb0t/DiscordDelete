import requests
import base64
import sys
import time

class Discord:
    def __init__(self):
        self.token = ""
        self.channelId = ""
        self.userId = ""
        self.deletedMessages = 0
        self.lastMessage = None
    
    def getRecentMessages(self):
        MESSAGE_LIST = []

        headers = {
            'authority': 'discord.com',
            'authorization': self.token,
            'accept-language': 'en-GB',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
            'accept': '*/*',
            'referer': 'https://discord.com/channels/@me',
        }
        if self.lastMessage == None:
            params = (
                ('limit', '100'),
            )
        else:
            params = (
                ('limit', '100'),
                ('before', self.lastMessage["id"])
            )
        response = requests.get(f'https://discord.com/api/v8/channels/{self.channelId}/messages', headers=headers, params=params)

        try:
            response.json()[0]
            for message in response.json():
                try:
                    message["author"]["id"]
                    MESSAGE_LIST.append(message)
                except:
                    continue
        except:
            print(response.json())
            return False

        self.lastMessage = MESSAGE_LIST[-1]
        return MESSAGE_LIST

    def deleteMessage(self, messageId):
        headers = {
            'authority': 'discord.com',
            'authorization': self.token,
            'accept-language': 'en-GB',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.309 Chrome/83.0.4103.122 Electron/9.3.5 Safari/537.36',
            'accept': '*/*',
        }
        response = requests.delete(f'https://discord.com/api/v8/channels/{self.channelId}/messages/{messageId}', headers=headers)

        if response.status_code == 204:
            return True
        elif response.status_code == 429:
            retry_after = response.json().get('retry_after', 0)
            print(f'[INFO] Rate Limit hit, retrying after {retry_after} seconds.')
            time.sleep(retry_after)
            return False
        elif response.status_code == 403:
            print(f"[INFO] Failed to delete message {messageId}, permissions issue (403). Skipping...")
            return True
        elif response.status_code == 404:
            print(f"[INFO] Message {messageId} already deleted or not found.")
            return True
        else:
            print(f"[ERROR] Failed to delete message {messageId}, Status code: {response.status_code}")
            return False

    def testToken(self):
        headers = {
            'authority': 'discord.com',
            'authorization': self.token,
            'accept-language': 'en-GB',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.309 Chrome/83.0.4103.122 Electron/9.3.5 Safari/537.36',
            'accept': '*/*',
        }

        response = requests.get('https://discord.com/api/v8/users/@me/connections', headers=headers)
        if response.status_code == 200:
            token_header = self.token.split(".")[0]
            missing_padding = len(token_header) % 4
            if missing_padding:
                token_header += "=" * (4 - missing_padding)
            self.userId = base64.b64decode(token_header).decode("utf-8")
            return True
        elif response.status_code == 401:
            return False
        else:
            print(response.status_code)
            return False


discord = Discord()
discord.token = input("[INPUT] Discord Token: ")

tokenStatus = discord.testToken()
if tokenStatus == True:
    print("[INFO] Working Token")
else:
    print("[INFO] Invalid Token - Quitting")
    sys.exit(0)

discord.channelId = input("[INPUT] Channel ID: ")

while True:
    try:
        messageBatch = discord.getRecentMessages()
        if messageBatch == False:
            print("[INFO] Error while fetching messages, stopping...")
            break
        else:
            pass

        for message in messageBatch:
            if str(discord.userId) == str(message["author"]["id"]):
                status = discord.deleteMessage(message["id"])
                if status == True:
                    discord.deletedMessages += 1
                    print(f'[{str(discord.deletedMessages)}] Successfully Deleted Message, ID: {str(message["id"])}')
                    time.sleep(0.2)
                else:
                    print(f'[{str(discord.deletedMessages)}] Failed to delete message {str(message["id"])}\n[INFO] Retrying shortly')
                    time.sleep(10)

        print("\n[INFO] Done with current batch, waiting 1 minute\n")
        time.sleep(60)

    except KeyboardInterrupt:
        print("\n[INFO] Script interrupted by user, exiting...")
        sys.exit(0)
