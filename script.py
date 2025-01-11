import asyncio

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv
import logging

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('discord')

words = ["maroc", "casa", "salut", "orange", "math", "element", "pomme"]
alphabets = [chr(x) for x in range(ord('a'), ord('z')+1)]
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
GAME_CHANNEL_ID = 1321990636169330778

game_state = {
    "players": [],
    "previousWords": "",
    "words": [],
    "currentPlayer": 0,
    "lastMsgSentOn": datetime.now(),
    "forbiddenChar": '',
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
                        await ctx.send("1 more player is needed to start the game.")
                    else :
                        await ctx.send(f"{numberOfPlayers - len(game_state['players'])} more players needed to start the game.")

            else:
                await ctx.send(f"{ctx.author.mention} You are already playing in this game.")


@bot.command()
async def stop(ctx):
    global game_state
    if ctx.channel.id == GAME_CHANNEL_ID:
        if gameIsStarted :
            if ctx.author not in game_state["players"]:
                await ctx.send(f"Sorry @{ctx.author.name} you aren't playing in this game, so you are not allowed to send commands or messages")
            else :
                await ctx.send(f"{ctx.author.mention}Stopping game...")
                game_state["players"].clear()
                game_state["current"] = 0
                game_state["words"].clear()
                await ctx.send(f"{ctx.author.mention}Successfully stopped the game...")
        else :
            await ctx.send(f"Sorry no game is started.")




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
                if message.content in game_state["words"]:
                    await message.channel.send(f"Oops that's been already used, Sorry {game_state['players'][game_state['currentPlayer']].mention} You'll be eliminated")
                    eliminate_player(game_state["currentPlayer"])
                    await continue_game(message.channel)
                word = message.content = message.content.lower().split()
                if len(word) > 1 :
                    await message.channel.send("You should enter a single word.")
                elif len(word[0]) < 3 :
                    await message.channel.send("You should enter a single word containing at least 3 characters.")
                else :
                    if word[0][0] != game_state["previousWord"][-1] or game_state["forbiddenChar"] in word[0]:
                        await message.channel.send(f"Oops that's not valid, Sorry {game_state['players'][game_state['currentPlayer']].mention} You'll be eliminated")
                        eliminate_player(game_state["currentPlayer"])
                        await continue_game(message.channel)
                    else :
                        game_state["previousWord"] = word[0]
                        game_state["words"].append(word[0])
                        await continue_game(message.channel)


    await bot.process_commands(message)


async def start_game(channel):
    global game_state
    global gameIsStarted
    gameIsStarted = True
    game_state["previousWord"] = random.choice(words)
    game_state["forbiddenChar"] = random.choice(alphabets)
    await channel.send(f"Game started! first word is {game_state['previousWord']}, and forbidden alphabet is {game_state['forbiddenChar']}.")
    await channel.send(f"{game_state['players'][game_state['currentPlayer']].mention} it's you're turn, you have 10 sec the previous word is {game_state['previousWord']}!")
    game_state["lastMsgSentOn"] = datetime.now()
    await asyncio.sleep(10)
    if datetime.now() - game_state["lastMsgSentOn"] >= timedelta(seconds=10):
        await channel.send(f"{game_state['players'][game_state['currentPlayer']].mention} {game_state['currentPlayer']} 10 sec passed without a response you've lost")
        eliminate_player(game_state["currentPlayer"])
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
            await channel.send(f"{game_state['players'][game_state['currentPlayer']].mention} it's you're turn, you have 10 sec the previous word is {game_state['previousWord']}!")
            game_state["lastMsgSentOn"] = datetime.now()
            await asyncio.sleep(10)
            if datetime.now() - game_state["lastMsgSentOn"] >= timedelta(seconds=10):
                await channel.send(f"{game_state['players'][game_state['currentPlayer']].mention} 10 sec passed without a response you've lost")
                eliminate_player(game_state["currentPlayer"])
                await continue_game(channel)


def eliminate_player(current:int):
    global game_state
    game_state["players"].pop(current)



async def end_game(channel):
    global game_state
    global gameIsStarted
    await channel.send("Game ended!")
    await channel.send(f"Congrats {game_state['players'][0].mention} you're the winnner !")
    gameIsStarted = False
    game_state["players"].clear()
    game_state["words"].clear()
    game_state["currentPlayer"] = 0




bot.run(TOKEN)







