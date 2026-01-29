## uvicorn api:app --reload --port 5000


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
import requests
from ai_client import AzureAIClient
from orchestrator_agent import OrchestratorAgent
from form_transformer import FormTransformer
from llm_metadata_extractor import (
    fetch_openapi,
    extract_all_capabilities,
    extract_form_fields_from_schema,
    get_capability_by_intent,
    INTENT_MAP
)
from routes.text_ai import router as text_ai_router
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# -------------------------
# App setup
# -------------------------
load_dotenv()
app = FastAPI(title="HRMS Orchestrator API")

origins = [
    "http://localhost:3000",   # React / Next.js
    "http://localhost:5173",   # Vite
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"]
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],          # Authorization, Content-Type, etc
)

app.include_router(text_ai_router)

# -------------------------
# Initialize once (VERY IMPORTANT)

ai_client = AzureAIClient(
    endpoint=os.getenv("AZURE_AI_ENDPOINT"),
    api_key=os.getenv("AZURE_AI_KEY"),
    model="gpt-4.1-mini"
)

orchestrator = OrchestratorAgent(ai_client)
form_transformer = FormTransformer(ai_client)

openapi_spec = fetch_openapi()
capabilities = extract_all_capabilities(openapi_spec, INTENT_MAP)

# -------------------------
# Request / Response Models
# -------------------------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: dict


# -------------------------
# WEBSOCKET Endpoint
# -------------------------
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            user_message = data.get("message")

            if not user_message:
                await websocket.send_json({
                    "type": "message",
                    "text": "Empty message received."
                })
                continue

            # 🔹 Orchestrator decides chat vs intent
            orchestrator_response = orchestrator.process(user_message)

            # -------------------------
            # CASE 1: GENERAL CHAT
            # -------------------------
            if orchestrator_response.type == "chat":
                await websocket.send_json({
                    "type": "message",
                    "text": orchestrator_response.reply
                })
                continue

            # CASE 2: TOOL (SEND EMAIL)
            # -------------------------
            if orchestrator_response.type == "tool" and orchestrator_response.tool == "send_email":
                await websocket.send_json({
                    "type": "tool",
                    "text": orchestrator_response.text
                })
                continue

            # -------------------------
            # CASE 2: HR INTENT
            # -------------------------
            if orchestrator_response.type == "intent":
                intent = orchestrator_response.intent

                print("INTENT RECEIVED:", intent)

                # SPECIAL CASE: GET leave calendar
                # ----------------------------------
                if intent == "get_leave_calendar":
                    try:
                        response = requests.get(
                            "http://localhost:8001/leave/calender"  # adjust if needed
                        )
                        response.raise_for_status()

                        await websocket.send_json({
                            "type": "table",
                            "text": response.json()
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "message",
                            "text": "Failed to fetch leave calendar."
                        })

                    continue

                # SPECIAL CASE: GET all employees
                # ----------------------------------
                if intent == "get_all_employees":
                    try:
                        response = requests.get(
                            "http://localhost:8001/employee/employees"
                        )
                        response.raise_for_status()

                        await websocket.send_json({
                            "type": "table",
                            "text": response.json()
                        })
                    except Exception:
                        await websocket.send_json({
                            "type": "message",
                            "text": "Failed to fetch employee list."
                        })

                    continue

                # SPECIAL CASE: GET pending leaves
                # ----------------------------------
                if intent == "get_pending_leaves":
                    try:
                        response = requests.get(
                            "http://localhost:8001/leave/pending/leave"
                        )
                        response.raise_for_status()

                        await websocket.send_json({
                            "type": "table",
                            "text": response.json()
                        })
                    except Exception:
                        await websocket.send_json({
                            "type": "message",
                            "text": "Failed to fetch pending leaves."
                        })

                    continue

                # SPECIAL CASE: GET upcoming (approved) leaves
                # ----------------------------------
                if intent == "get_upcoming_leaves":
                    try:
                        response = requests.get("http://localhost:8001/leave/details")
                        response.raise_for_status()

                        leaves = response.json()

                        approved_leaves = [
                            leave for leave in leaves
                            if leave.get("status") == "approved"
                        ]

                        if approved_leaves:
                            await websocket.send_json({
                                "type": "table",
                                "text": approved_leaves
                            })
                        else:
                            await websocket.send_json({
                                "type": "message",
                                "text": "You have no upcoming approved leaves."
                            })

                    except Exception:
                        await websocket.send_json({
                            "type": "message",
                            "text": "Failed to fetch leave details."
                        })

                    continue

                # DEFAULT CASE: FORM-BASED HR INTENTS
                capability = get_capability_by_intent(capabilities, intent)

                if not capability:
                    await websocket.send_json({
                        "type": "message",
                        "text": "Sorry, I can't handle this request yet."
                    })
                    continue

                raw_fields = extract_form_fields_from_schema(
                    openapi_spec,
                    capability["schema"]
                )

                schema_form = {
                    "type": "form",
                    "intent": intent,
                    "action": {
                        "method": capability["method"],
                        "path": capability["path"]
                    },
                    "fields": raw_fields
                }

                try:
                    ui_form = form_transformer.transform(schema_form)
                except Exception:
                    ui_form = schema_form

                await websocket.send_json(ui_form)
                continue

            # Fallback
            await websocket.send_json({
                "type": "message",
                "text": "Sorry, I didn’t understand that."
            })

    except WebSocketDisconnect:
        print("Client disconnected")




# @app.post("/chat", response_model=ChatResponse)
# def chat(req: ChatRequest):
#     try:
#         # STEP A: Orchestrator decides chat vs intent
#         # intent_response = orchestrator.detect_intent(req.message)
#         # intent = intent_response.intent

#         orchestrator_response = orchestrator.process(req.message)

#         if orchestrator_response.type == "chat":
#             return ChatResponse(response={
#                 "type": "message",
#                 "text": orchestrator_response.reply
#             })
        
#         # CASE 2: HR INTENT
#         # -------------------------
#         if orchestrator_response.type == "intent":
#             intent = orchestrator_response.intent

#             # STEP B: Find capability
#             capability = get_capability_by_intent(capabilities, intent)

#             if not capability:
#                 return ChatResponse(response={
#                     "type": "message",
#                     "text": "Sorry, I can't handle this request yet."
#                 })

#             # STEP C: Extract schema fields
#             raw_fields = extract_form_fields_from_schema(
#                 openapi_spec,
#                 capability["schema"]
#             )

#             schema_form = {
#                 "type": "form",
#                 "intent": intent,
#                 "action": {
#                     "method": capability["method"],
#                     "path": capability["path"]
#                 },
#                 "fields": raw_fields
#             }

#             # STEP D: Transform to UI form
#             try:
#                 ui_form = form_transformer.transform(schema_form)
#             except Exception:
#                 ui_form = schema_form

#             return ChatResponse(response=ui_form)
        
#         return ChatResponse(response={
#             "type": "message",
#             "text": "Sorry, I didn’t understand that."
#         })

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
