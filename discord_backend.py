import os
import logging
import asyncio
import datetime
import boto3
import discord 
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
AGENT_ID = os.getenv("AGENT_ID")
ALIAS_ID = os.getenv("ALIAS_ID")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

client=boto3.client(
            service_name="bedrock-agent-runtime",
            region_name="us-east-1") 

def split_message(answer):
    messages = []
    chunk_size = 1900  # Discord message character limit
    for i in range(0, len(answer), chunk_size):
        split = answer[i:i + chunk_size]
        last_period = split.rfind('.')
        if last_period != -1:
            sub_message = answer[i:last_period + 1]  # Include the period in the sub-message
        elif last_period == -1: 
            sub_message = split# If no period found, take the whole chunk
        print(f"Sub-message: {sub_message}")
        messages.append(sub_message)
        i += last_period + 1
    return messages


@bot.event
async def on_ready():
    logger.debug(f"Bot is ready. Logged in as {bot.user.name} ({bot.user.id})")
    
@bot.event
async def on_message(message):
    logger.debug(f"Received message: {message.content} from {message.author} at {datetime.datetime.now()}")
    if message.author == bot.user:
        return
    if message.content.startswith('!Hello'):
        async with message.channel.typing():
            await asyncio.sleep(1) #simulate processing time
            response = "Hello, I am the Hallucination Allocation Machine, but you can call me H.A.M.!"
            logger.debug(f"Sending response: {response} to {message.channel}")
            await message.channel.send(response)
    elif message.content.startswith('!HAM '):
        async with message.channel.typing():
            response = invoke_agent(client, message.content, str(message.author.id), AGENT_ID, ALIAS_ID)
            messages = split_message(response)
            for msg in messages:
                await message.channel.send(msg)
                
def invoke_agent(client, prompt, session_id, agent_id = AGENT_ID, alias_id = ALIAS_ID):
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            enableTrace=True,
            sessionId = session_id,
            inputText=prompt,
            streamingConfigurations = { 
    "applyGuardrailInterval" : 20,
      "streamFinalResponse" : False
            }
        )
        completion = ""
        for event in response.get("completion"):
            #Collect agent output.
            if 'chunk' in event:
                chunk = event["chunk"]
                completion += chunk["bytes"].decode()
            
            # Log trace output.
            if 'trace' in event:
                trace_event = event.get("trace")
                trace = trace_event['trace']
                for key, value in trace.items():
                    logging.info("%s: %s",key,value)

        logger.info(f"Agent response: {completion}")
        return completion
        
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN is not set in the environment variables.") 
    
    logger.debug("Starting Discord bot...")
    bot.run(DISCORD_TOKEN)
    