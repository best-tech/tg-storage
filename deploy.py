from telethon import TelegramClient, utils
from telethon.sessions.string import StringSession
import json
import webbrowser


def main():
    api_id = input('Enter API_ID:')
    api_hash = input('Enter API_HASH:')

    client = TelegramClient(api_id, int(api_id), api_hash)

    client.start()
    client.disconnect()


if __name__ == '__main__':
    main()
