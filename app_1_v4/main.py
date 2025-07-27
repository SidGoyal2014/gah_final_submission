import ast
import os
import json
import asyncio
import base64
import warnings
from datetime import datetime
from google.genai import types
from google import genai
from vertexai import agent_engines
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
    Blob,
)

from google.adk.runners import InMemoryRunner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig

from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError

from google_search_agent.agent import root_agent

import contextvars
from typing import Optional

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

load_dotenv()

APP_NAME = "ADK Streaming example"

session_service = None

import vertexai

# conversations = []

client = vertexai.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)

client1 = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)

agent_engine_id = os.getenv("agent_engine_id")


user_id_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('user_id', default=None)

def get_current_user_id() -> Optional[str]:
    """Get the current user ID from context"""
    return user_id_context.get()

def set_current_user_id(user_id: str):
    """Set the current user ID in context"""
    user_id_context.set(user_id)

async def start_agent_session(user_id, is_audio=False):
    """Starts an agent session with working memory integration"""

    print(f"\n🚀 Starting agent session for user: {user_id}")

    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
    )
    print(f"✅ Session created: {session.id}")

    # Configure run settings
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    print(f"🚀 Starting live agent session...")
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )

    print(f"✅ Agent session started successfully")
    return live_events, live_request_queue, session


async def agent_to_client_messaging(websocket, live_events):
    """Agent to client communication"""
    try:
        while True:
            async for event in live_events:

                if event.turn_complete or event.interrupted:
                    message = {
                        "turn_complete": event.turn_complete,
                        "interrupted": event.interrupted,
                    }
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: {message}")
                    continue

                # Read the Content and its first Part
                part: Part = (
                        event.content and event.content.parts and event.content.parts[0]
                )
                if not part:
                    continue

                # If it's audio, send Base64 encoded audio data
                is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
                if is_audio:
                    audio_data = part.inline_data and part.inline_data.data
                    if audio_data:
                        message = {
                            "mime_type": "audio/pcm",
                            "data": base64.b64encode(audio_data).decode("ascii")
                        }
                        await websocket.send_text(json.dumps(message))
                        # conversations.append( {"role": "agent", "content": audio_data} )
                        print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                        continue

                # If it's text and a partial text, send it
                if part.text and event.partial:
                    message = {
                        "mime_type": "text/plain",
                        "data": part.text
                    }
                    await websocket.send_text(json.dumps(message))
                    # conversations.append({"role": "agent", "content": message["data"]})
                    print(f"[AGENT TO CLIENT]: text/plain: {message}")

    except WebSocketDisconnect:
        print("[AGENT TO CLIENT]: WebSocket disconnected")
    except Exception as e:
        print(f"[AGENT TO CLIENT]: Unexpected error: {e}")


async def client_to_agent_messaging(websocket, live_request_queue, user_id: str):
    """Client to agent communication with user context"""
    # Set user_id in context for this task
    # set_current_user_id(user_id)

    try:
        while True:
            # Decode JSON message
            message_json = await websocket.receive_text()
            message = json.loads(message_json)
            mime_type = message["mime_type"]
            data = message["data"]

            # Send the message to the agent
            if mime_type == "text/plain":
                # Send a text message
                data = "userid: " + user_id + "  message: " + message["data"]
                content = Content(role="user", parts=[Part.from_text(text=data)])
                live_request_queue.send_content(content=content)
                # conversations.append({"role": "user", "content": message["data"]})
                print(f"[CLIENT TO AGENT]: {data}")
            elif mime_type == "audio/pcm":
                # Send an audio data
                # conversations.append({"role": "agent", "content": message["data"]})
                decoded_data = base64.b64decode(data)
                live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
            else:
                raise ValueError(f"Mime type not supported: {mime_type}")

    except WebSocketDisconnect:
        print("[CLIENT TO AGENT]: WebSocket disconnected")
    except Exception as e:
        print(f"[CLIENT TO AGENT]: Unexpected error: {e}")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_sessions = {}
RESOURCE_ID = os.getenv("RESOURCE_ID")


class MessageRequest(BaseModel):
    user_id: str
    message: str

# STATIC_DIR = Path("static")
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Serves the index.html"""
    return "all good, lets go! All the best!"
    # return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.post("/analyze-image/")
async def analyze_image(request: Request):
    body = await request.json()
    base64image = body.get("base64image")

    if not base64image:
            return {"error": "Missing 'base64image' field in JSON body"}

    response = client1.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=base64image, mime_type="image/png"),
            """
            You are a smart and reliable digital farming assistant, designed to support farmers.

            1. Analyze the image and identify what it shows — it could be:
               - Soil, plants, crops, pests, disease, irrigation system, weather damage, farm tools, etc.

            2. Based on your observation, provide useful insights:
               - If it’s a crop: its health, stage of growth, and any signs of stress or disease.
               - If it’s soil: soil type, condition, and suitable crops.
               - If it’s pests or disease: identify them and suggest treatment.
               - If it’s farm infrastructure: check for any problems or inefficiencies.

            3. Give actionable advice** in simple language:
               - What should the farmer do next?
               - Any precautions or treatments?
               - Any tools or resources that could help?"""
        ]
    )
    return response.text

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, is_audio: str):
    """Enhanced WebSocket endpoint with working memory integration"""

    # Wait for client connection
    await websocket.accept()
    print(f"\n🔌 Client #{user_id} connected, audio mode: {is_audio}")

    # Send periodic pings to keep connection alive in Cloud Run
    async def heartbeat():
        try:
            while True:
                await asyncio.sleep(30)  # Send ping every 30 seconds
                await websocket.send_text("ping")
        except (WebSocketDisconnect, ConnectionClosedError):
            pass
        except Exception as e:
            print(f"Heartbeat error: {e}")

    heartbeat_task = None
    live_request_queue = None
    session_ = None

    try:
        # Start agent session with memory integration
        user_id_str = str(user_id)
        live_events, live_request_queue, session_ = await start_agent_session(user_id_str, is_audio == "true")

        # Start heartbeat task to keep connection alive
        heartbeat_task = asyncio.create_task(heartbeat())

        # Start messaging tasks
        agent_to_client_task = asyncio.create_task(
            agent_to_client_messaging(websocket, live_events)
        )
        client_to_agent_task = asyncio.create_task(
            client_to_agent_messaging(websocket, live_request_queue, user_id_str)
        )

        # Wait until the websocket is disconnected or an error occurs
        tasks = [agent_to_client_task, client_to_agent_task, heartbeat_task]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Handle completed tasks and check for exceptions
        for task in done:
            try:
                await task  # This will re-raise any exceptions
            except WebSocketDisconnect:
                print(f"Client #{user_id}: WebSocket disconnected normally")
            except Exception as e:
                print(f"Client #{user_id}: Task completed with error: {e}")

    except WebSocketDisconnect:
        print(f"Client #{user_id}: WebSocket disconnected during setup")
    except Exception as e:
        print(f"Client #{user_id}: Unexpected error in websocket endpoint: {e}")
    finally:
        # Clean up resources
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

        if live_request_queue:
            live_request_queue.close()

        print(f"🔌 Client #{user_id} disconnected and cleaned up")
        # save_conversation(user_id, conversations)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "session_service": "initialized" if session_service else "not_initialized",
        "timestamp": datetime.now().isoformat()
    }

import os

port = int(os.environ.get("PORT", 8082))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
