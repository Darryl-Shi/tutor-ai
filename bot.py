from dotenv import load_dotenv
import os
import json
import asyncio
import time
import discord as pycord
from discord.ext import commands

from main import TutorAI

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
intents = pycord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.remove_command('help')

tutor_instances = {}  # dictionary to store TutorAI instances

@bot.event
async def on_ready():
    print(f'{bot.user} is connected')

@bot.command(name='learn')
async def start_conversation(ctx, topic=None):
    if topic:
        existing_threads = ctx.channel.threads
        for thread in existing_threads:
            if thread.name == f"{ctx.author.name}'s {topic} session":
                await ctx.send(f"You already have an active session on {topic}. Please use that instead.")
        # create a new thread to start the conversation
        thread = await ctx.channel.create_thread(name=f"{ctx.author.name}'s {topic} session"); print("Thread created")

        if topic not in tutor_instances:
            tutor_instances[topic] = TutorAI()
            print(tutor_instances)
        tutor = tutor_instances[topic]
        tutor.add_topic(topic)
        i = 0  # start at stage 1
        await tutor.chat(topic, i, thread) # convert stage number to string before passing to chat method
        await thread.send("Any further command can be run by responding to the first message!")
        await thread.send("To end the session, type !reset")
        await thread.send(ctx.author.mention)
        while True:
            try:
                user_input = await bot.wait_for('message_create', check=lambda m: m.author == ctx.author and m.channel == thread, timeout=120.0)
                if user_input.content.lower() == "next":
                    async with thread.typing():
                        i += 1
                        asyncio.create_task(tutor.chat(topic, i, thread))
                        await thread.send("To end the session, type !reset")
                else:
                    async with thread.typing():
                        asyncio.create_task(tutor.custom_chat(topic, user_input.content, thread))
                        await thread.send("To end the session, type !reset")
            except asyncio.TimeoutError:
                await thread.send("Conversation timed out.")
                del tutor_instances[topic]  # remove the instance from the dictionary
                await thread.delete()  # delete the thread
                break
    else:
        await ctx.send("To see what I can do, please use !help")

@bot.command(name='reset')
async def reset_conversation(ctx):
    thread = ctx.channel
    topic = thread.name.split("'s ")[1].split(" session")[0]
    if topic in tutor_instances:
        tutor = tutor_instances[topic]
        tutor.reset(topic)
        await thread.send("Deleting chat and resetting to defaults...")
        await thread.delete()
        del tutor_instances[topic]  # remove the instance from the dictionary
    else:
        await thread.send("No conversation to reset.")



@bot.command(name='help')
async def display_help(ctx):
    help_msg = "To start a conversation with me, use the !learn command followed by the topic you want to learn about. For example: `!learn python`.\n\nWhile in a conversation with me, you can enter the following commands:\n\n`next`: move to the next stage of the conversation\n`reset`: reset the conversation to the default stage\n`exit`: end the conversation\n\nYou can also reply to any other message to send it to me and continue the conversation."
    await ctx.send(help_msg)

bot.run(TOKEN)