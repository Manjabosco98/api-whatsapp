import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Evolution Webhook API")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "whatsapp_joao")
WHATSAPP_GROUP_JID = os.getenv("WHATSAPP_GROUP_JID")

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

app = FastAPI(title=APP_NAME)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": APP_NAME,
        "message": "Webhook FastAPI está rodando dentro do Docker",
    }


@app.post("/webhook/evolution")
async def receive_evolution_webhook(request: Request):
    payload: dict[str, Any] = await request.json()

    event = payload.get("event")
    instance = payload.get("instance")
    data = payload.get("data", {})

    print("=" * 80)
    print("WEBHOOK RECEBIDO")
    print("Horário:", datetime.now().isoformat())
    print("Evento:", event)
    print("Instância:", instance)

    save_payload(payload)

    if event == "MESSAGES_UPSERT":
        handle_message_upsert(data)

    elif event in {
        "CHATS_UPSERT",
        "CHATS_UPDATE",
        "GROUPS_UPSERT",
        "GROUP_UPDATE",
        "GROUP_PARTICIPANTS_UPDATE",
    }:
        handle_chat_or_group_update(event, data)

    return JSONResponse(
        content={
            "status": "received",
            "event": event,
            "instance": instance,
        },
        status_code=200,
    )


def save_payload(payload: dict[str, Any]) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    event = payload.get("event", "unknown")

    filename = LOG_DIR / f"{timestamp}_{event}.json"

    filename.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def handle_message_upsert(data: dict[str, Any]) -> None:
    key = data.get("key", {})

    remote_jid = key.get("remoteJid")
    message_id = key.get("id")
    from_me = key.get("fromMe")

    push_name = data.get("pushName")
    message_type = data.get("messageType")
    message = data.get("message", {})

    print("Mensagem recebida")
    print("Remote JID:", remote_jid)
    print("Message ID:", message_id)
    print("From me:", from_me)
    print("Push name:", push_name)
    print("Message type:", message_type)

    if remote_jid and remote_jid.endswith("@g.us"):
        print("Mensagem veio de grupo.")

    if WHATSAPP_GROUP_JID and remote_jid != WHATSAPP_GROUP_JID:
        print("Mensagem ignorada: não pertence ao grupo monitorado.")
        return

    if message_type == "conversation":
        text = message.get("conversation")
        print("Texto:", text)

    elif message_type in {
        "documentMessage",
        "imageMessage",
        "videoMessage",
        "audioMessage",
        "stickerMessage",
    }:
        print("Mensagem com mídia/arquivo detectada.")
        print("Tipo:", message_type)

    else:
        print("Tipo de mensagem não tratado ainda:", message_type)


def handle_chat_or_group_update(event: str, data: dict[str, Any]) -> None:
    print("Evento de chat/grupo recebido:", event)

    remote_jid = (
        data.get("remoteJid")
        or data.get("id")
        or data.get("jid")
    )

    name = (
        data.get("pushName")
        or data.get("name")
        or data.get("subject")
    )

    print("Remote JID:", remote_jid)
    print("Nome:", name)