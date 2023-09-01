from dotenv import load_dotenv
import requests
import discord
import asyncio
import decimal
import os

load_dotenv()


TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = os.environ["DISCORD_SERVER_ID"]
DECIMAL_PLACES = 2  # Adjust as needed


def get_account_balance() -> decimal.Decimal:
    """
    Fetch balance from Hedera account
    """
    while True:
        r = requests.get('https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/0.0.2997590')
        if r.status_code == 200:
            data = r.json()
            return decimal.Decimal(data['balance']['balance'])
        else:
            print(r.status_code)
            asyncio.sleep(100)  # Sleep for 100 seconds before retrying


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


async def send_update(balance: decimal.Decimal, numDecimalPlace=None):
    if numDecimalPlace is not None:
        balance = round(balance, numDecimalPlace) / 100000000 # Convert from TH to H
        balance_str = format(balance, f'.{numDecimalPlace}f')
    else:
        balance_str = format(balance, '.1f')

    guild = client.get_guild(int(GUILD_ID))
    if guild:
        await guild.me.edit(nick=f'{balance_str} HBAR')

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Treasure Chest"))
    await asyncio.sleep(10000)  # 24 hours


@client.event
async def on_ready():
    """
    When discord client is ready
    """
    while True:
        balance = get_account_balance()
        await send_update(balance, DECIMAL_PLACES)


client.run(TOKEN)
