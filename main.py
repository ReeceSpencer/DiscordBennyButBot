import settings
import discord
import random
import requests
import string
import asyncio
from discord.ext import commands

def run():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='$', intents=intents)

    @bot.hybrid_command(name='ping')
    async def ping(context):
        await context.send('pong!')

    @bot.hybrid_command(name='dice')
    async def dice(context, arg = ''):
        diceSize = int(arg) if arg.isdecimal() else 6
        await context.send(f'rolling d{diceSize}: {random.randint(1, diceSize)}')

    @bot.hybrid_command(name='mtghangman')
    async def mtghangman(context):
        response = requests.get("https://api.scryfall.com/cards/random")
        if response.status_code == 200:
            active = True

            incorrectGuesses = 0
            correctGuesses = 0
            maxIncorrectGuesses = 6
            data = response.json()
            cardName = data["name"]
            print(cardName)
            if len(cardName) > 0 and type(cardName) is str:
                cardNameList = list(cardName)
                cardNameLetters = [x for x in list(set(cardName.lower())) if x in string.ascii_letters]
                print(''.join(cardNameLetters))
                guesses = []

                cardDisplay = []
                for char in cardNameList:
                    if char.isalpha():
                        cardDisplay.append('\_')
                    elif char.isspace():
                        cardDisplay.append(char)
                    else:
                        cardDisplay.append(f'\{char}')
                
                print(' '.join(cardDisplay))

                await context.send(f'Game Start!\nYou have 1 minute per response\n{' '.join(cardDisplay)}')

                while active:
                    try:
                        userResponse = await bot.wait_for("message", check=lambda m: m.author == context.author, timeout = 60)
                        userResponseText = userResponse.content.lower()
                        if len(userResponseText) == 1 and userResponseText.isalpha:
                            if userResponseText in guesses:
                                await context.send(f'Already guessed `{userResponseText}`\n{' '.join(cardDisplay)}')
                            else:
                                guesses.append(userResponseText)
                                if userResponseText in cardNameLetters:
                                    matchingIndexList = [i for i, x in enumerate(cardNameList) if x.lower() == userResponseText]
                                    for i in matchingIndexList:
                                        cardDisplay[i] = cardNameList[i]
                                    await context.send(f'{' '.join(cardDisplay)}')
                                    correctGuesses += 1
                                    if len(cardNameLetters) == correctGuesses:
                                        await context.send(f'**{context.author.nick}** wins!\nGame Over!')
                                        active = False
                                        continue
                                else:
                                    incorrectGuesses += 1
                                    if incorrectGuesses < maxIncorrectGuesses:
                                        await context.send(f'Incorrect guesses: {incorrectGuesses}/{maxIncorrectGuesses}\n{' '.join(cardDisplay)}')
                                    else:
                                        await context.send(f'Incorrect guesses: {incorrectGuesses}/{maxIncorrectGuesses}\nGame Over!\n{cardName}')
                                        active = False
                                        continue
                        else:
                            await context.send('Incorrect response format')
                    except asyncio.TimeoutError:
                        await context.send(f'No response, Game Over\n{cardName}')
                        active = False
                        continue
            else:
                await context.send('Name generation failed')
        else:
            await context.send('API connection failed')

    bot.run(settings.DISCORD_API_TOKEN)

if __name__ == "__main__":
    run()