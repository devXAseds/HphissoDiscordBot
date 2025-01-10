import asyncio

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random

words = ["maroc", "casa", "salut", "orange", "math", "element", "pomme"]

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
GAME_CHANNEL_ID = 1321990636169330778

game_state = {
    "players": [],
    "previousWords": "",
    "currentPlayer": 0,
    "lastMsgSentOn": datetime.now(),
    "forbiddenChar": 'm',
}
numberOfPlayers = 2
gameIsStarted = False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm your game bot.")

@bot.command()
async def start(ctx):
    if ctx.channel.id == GAME_CHANNEL_ID:
        if gameIsStarted :
            if ctx.author not in game_state["players"]:
                await ctx.send(f"Sorry @{ctx.author.name} you aren't playing in this game, so you are not allowed to send commands or messages")
            else :
                await ctx.send(f"{ctx.author.mention} Game is already being played.")
        else :
            if ctx.author not in game_state["players"]:
                game_state["players"].append(ctx.author)
                if len(game_state["players"]) == numberOfPlayers:
                    await start_game(ctx.channel)
                else :
                    if len(game_state["players"]) == numberOfPlayers-1 :
                        await ctx.send("1 more player needed to start the game.")
                    else :
                        await ctx.send(f"{numberOfPlayers - len(game_state["players"])} more players needed to start the game.")

            else:
                await ctx.send(f"{ctx.author.mention} You are already playing in this game.")




@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  #we added this so that the bot will ignore its own messages
    if message.channel.id == GAME_CHANNEL_ID: # checking if the channel the message is being sent in is the game channel or not
        if gameIsStarted :
            if message.author not in game_state["players"]:
                await message.channel.send(f"Sorry @{message.author.name} you aren't playing in this game, so you are not allowed to send commands or messages")
            elif message.author.id != game_state["players"][game_state["currentPlayer"]].id:
                await message.channel.send(f"{message.author.mention} it's not your turn.")
            else :
                word = message.content = message.content.lower().split()
                if len(word) > 1 :
                    await message.channel.send("You should enter a single word.")
                elif len(word[0]) < 3 :
                    await message.channel.send("You should enter a single word containing at least 3 characters.")
                else :
                    if word[0][0] != game_state["previousWord"][-1] or game_state["forbiddenChar"] in word[0]:
                        await message.channel.send(f"You should enter a single word containing at least 3 characters, starting with the last character of the previous word, and it shouldn't contain : {game_state["forbiddenChar"]}")
                    else :
                        game_state["previousWord"] = word[0]
                        await continue_game(message.channel)



    await bot.process_commands(message)


async def start_game(channel):
    global game_state
    global gameIsStarted
    gameIsStarted = True
    game_state["previousWord"] = random.choice(words)
    await channel.send(f"Game started! first word is {game_state['previousWord']}.")
    await channel.send(f"{game_state["players"][game_state["currentPlayer"]].mention} it's you're turn, you have 10 sec the previous word is {game_state['previousWord']}!")
    game_state["lastMsgSentOn"] = datetime.now()
    await asyncio.sleep(10)
    if datetime.now() - game_state["lastMsgSentOn"] >= timedelta(seconds=10):
        await channel.send(f"{game_state["players"][game_state["currentPlayer"]].mention} {game_state["currentPlayer"]} 10 sec passed without a response you've lost")
        game_state["players"].pop(game_state["currentPlayer"])
        if len(game_state["players"]) == 1:
            await end_game(channel)
        else:
            await continue_game(channel)



async def continue_game(channel):
    global game_state
    global gameIsStarted

    if len(game_state["players"]) > 0:
        if len(game_state["players"]) == 1:
            await end_game(channel)
        else:
            game_state["currentPlayer"] = (game_state["currentPlayer"] + 1) % len(game_state["players"])
            await channel.send(f"{game_state["players"][game_state["currentPlayer"]].mention} it's you're turn, you have 10 sec the previous word is {game_state['previousWord']}!")
            game_state["lastMsgSentOn"] = datetime.now()
            await asyncio.sleep(10)
            if datetime.now() - game_state["lastMsgSentOn"] >= timedelta(seconds=10):
                await channel.send(f"{game_state["players"][game_state["currentPlayer"]].mention} {game_state["currentPlayer"]} 10 sec passed without a response you've lost")
                game_state["players"].pop(game_state["currentPlayer"])
                await continue_game(channel)




async def end_game(channel):
    global game_state
    global gameIsStarted
    await channel.send("Game ended!")
    await channel.send(f"Congrats {game_state["players"][0].mention} you're the winnner !")
    gameIsStarted = False
    game_state["players"].clear()
    game_state["currentPlayer"] = 0




bot.run('MTMyMTQyNDY5NDM3NjY2NTE1MA.Gcdhx_.4sOsoJSV4EPr-hv4nTwSBkjG9z0_yyJNPxVZA0')







