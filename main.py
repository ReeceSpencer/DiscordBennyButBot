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

    # test response command
    @bot.hybrid_command(name='ping')
    async def ping(context):
        await context.send('pong!')

    # random number generator
    @bot.hybrid_command(name='dice')
    async def dice(context, arg = ''):
        diceSize = int(arg) if arg.isdecimal() else 6
        await context.send(f'rolling d{diceSize}: {random.randint(1, diceSize)}')

    # hangman game using MTG cards
    # Scryfall API connection for random card
    @bot.hybrid_command(name='mtghangman')
    async def mtghangman(context):
        response = requests.get("https://api.scryfall.com/cards/random")
        # check for successful API connection
        if response.status_code == 200:
            active = True

            incorrectGuesses = 0
            correctGuesses = 0
            maxIncorrectGuesses = 6
            data = response.json()
            cardName = data["name"]
            # Print card name for test purposes
            #print(cardName)
            if len(cardName) > 0 and type(cardName) is str:
                # List each character of card name
                cardNameList = list(cardName)
                # Unique list of all card name characters if it is an alpha character
                cardNameLetters = [x for x in list(set(cardName.lower())) if x in string.ascii_letters]
                # print unique letters for test purposes
                #print(''.join(cardNameLetters))
                guesses = []

                cardDisplay = []
                for char in cardNameList:
                    if char.isalpha():
                        # escape underline for hangman display in Discord
                        cardDisplay.append('\_')
                    elif char.isspace():
                        # print spaces to still be seen in Discord
                        cardDisplay.append(char)
                    else:
                        # escape any non-alpha characters for Discord
                        cardDisplay.append(f'\{char}')
                # print unique letters for test purposes
                #print(' '.join(cardDisplay))

                await context.send(f'Game Start!\nYou have 1 minute per response\n{' '.join(cardDisplay)}')

                # continue checking for input from same message author/user
                while active:
                    try:
                        userResponse = await bot.wait_for("message", check=lambda m: m.author == context.author, timeout = 60)
                        userResponseText = userResponse.content.lower()
                        if len(userResponseText) == 1 and userResponseText.isalpha:
                            if userResponseText in guesses:
                                await context.send(f'Already guessed `{userResponseText}`\n{' '.join(cardDisplay)}')
                            else:
                                guesses.append(userResponseText)
                                # if guessed correct
                                if userResponseText in cardNameLetters:
                                    matchingIndexList = [i for i, x in enumerate(cardNameList) if x.lower() == userResponseText]
                                    for i in matchingIndexList:
                                        cardDisplay[i] = cardNameList[i]
                                    await context.send(f'{' '.join(cardDisplay)}')
                                    correctGuesses += 1
                                    # if all letters are guessed correctly
                                    if len(cardNameLetters) == correctGuesses:
                                        # print user's name bolded for Discord
                                        await context.send(f'**{context.author.nick}** wins!\nGame Over!')
                                        active = False
                                        continue
                                else:
                                    # if guessed incorrectly
                                    incorrectGuesses += 1
                                    # tell user they guessed wrong or lose
                                    if incorrectGuesses < maxIncorrectGuesses:
                                        await context.send(f'Incorrect guesses: {incorrectGuesses}/{maxIncorrectGuesses}\n{' '.join(cardDisplay)}')
                                    else:
                                        await context.send(f'Incorrect guesses: {incorrectGuesses}/{maxIncorrectGuesses}\nGame Over!\n{cardName}')
                                        active = False
                                        continue
                        else:
                            # user didn't message a singlular alpha character
                            await context.send('Incorrect response format')
                    except asyncio.TimeoutError:
                        # user ran out of time
                        await context.send(f'No response, Game Over\n{cardName}')
                        active = False
                        continue
            else:
                # incase name is empty
                await context.send('Name generation failed')
        else:
            # if bad connection to API
            await context.send('API connection failed')
    # keep the API token secret
    bot.run(settings.DISCORD_API_TOKEN)

if __name__ == "__main__":
    run()