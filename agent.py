import boto3
import os
from dotenv import load_dotenv
import logging

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
AGENT_ID = os.getenv("AGENT_ID")
ALIAS_ID = os.getenv("ALIAS_ID")

    
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