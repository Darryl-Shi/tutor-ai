import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json

from main import TutorAI


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
tutor = TutorAI()

@bot.event
async def on_ready():
    print(f'{bot.user} is connected')
@bot.command(name='learn')
async def start_conversation(ctx, topic=None):
    if topic:
        tutor.topic = topic
        tutor.add_topic(tutor.topic)
        i = 0  # start at stage 1
        await tutor.chat(i, ctx)  # convert stage number to string before passing to chat method
        await ctx.send("Any further command can be run by responding to the first message!")
        while True:
            try:
                user_input = await bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=120.0)
                if user_input.content.lower() == "exit":
                    break
                if user_input.content.lower() == "next":
                    async with ctx.typing():
                        i += 1
                        await tutor.chat(i, ctx)
                else:
                    async with ctx.typing():
                        await tutor.custom_chat(user_input.content, ctx)  # also convert stage number to string here
            except asyncio.TimeoutError:
                await ctx.send("Conversation timed out.")
                break
    else:
        await ctx.send("Please specify a topic. Usage: !learn <topic>")
@bot.event()
async def on_message(message):
    if bot.user.mentioned_in(message):
        await ctx.send("Hi! To start learning, use the learn command. Any further command can be run by responding to the first message! Usage: !learn <topic>")
bot.run(TOKEN)
