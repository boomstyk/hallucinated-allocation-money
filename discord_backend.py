import os
import discord 
import logging
from dotenv import load_dotenv
from discord.ext import commands

logger = logging.getLogger("bot_logger")
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)

logger.addHandler(ch)

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.debug(f"Bot is ready. Logged in as {bot.user.name} ({bot.user.id})")
    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('!Hello'):
        await message.channel.send('Hello, I am the Hallucination Allocation Machine, but you can call me H.A.M.!')

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN is not set in the environment variables.") 
    
    logger.debug("Starting Discord bot...")
    bot.run(DISCORD_TOKEN)