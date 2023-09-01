from typing import List
import requests
import time
import json, yaml
import discord
import asyncio
import decimal

def get_price() -> dict:
    """
    Fetch price from Saucerswap API
    """
    while True:
        r = requests.get('https://api.saucerswap.finance/tokens')
        if r.status_code == 200:
            return r.json()
        else:
            print(r.status_code)
            time.sleep(10)

def main(ticker: str) -> None:

    # 1. Load config
    filename = 'crypto_config.yaml'
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.Loader)[ticker] # Get passed ticker from yaml file
        print(config)

    # 2. Connect w the bot
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    async def send_update(priceList, numDecimalPlace=None):
        if numDecimalPlace == 0:
            numDecimalPlace = None  # round(2.3, 0) -> 2.0 but we don't want ".0"

        price_now = priceList['priceUsd']

        if numDecimalPlace is not None:
            price_now = round(price_now, numDecimalPlace)
            price_now = format(decimal.Decimal(price_now), f'.{numDecimalPlace}f')
        else:
            # Format as standard decimal, not scientific notation
            price_now = format(decimal.Decimal(price_now), '.6f')

        for guildId in config['guildId']:
            await client.get_guild(guildId).me.edit(nick=f'${price_now}')

        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=ticker))
        await asyncio.sleep(config['updateFreq'])  # in seconds

    @client.event
    async def on_ready():
        """
        When discord client is ready
        """
        while True:
            # 3. Fetch price
            priceList = get_price()
            ssToken = []
            for token in priceList:
                if token['symbol'] == ticker:
                    ssToken = token

            print(ssToken)

            # 4. Feed it to the bot
            await send_update(ssToken, config['decimalPlace'][0])

    client.run(config['discordBotKey'])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--ticker',
                        action='store')
    args = parser.parse_args()
    main(ticker=args.ticker)
