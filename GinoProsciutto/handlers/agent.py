"""Ponte verso l'agente di manutenzione di status.enricocovili.com.

L'agente invia i report con la Bot API; i pulsanti (callback "agent:...") e le reply
ai suoi messaggi arrivano qui (Telethon) e vengono inoltrati al container status-agent,
pubblicato solo su 127.0.0.1 dell'host (questo bot gira in network_mode: host).
"""
import asyncio
import logging
import os

import requests
from telethon import events
from utils import Utils

AGENT_HOOK_URL = os.getenv("AGENT_HOOK_URL", "http://127.0.0.1:8091")
AGENT_HOOK_TOKEN = os.getenv("AGENT_HOOK_TOKEN", "")


def _post(path: str, payload: dict) -> dict:
    r = requests.post(
        f"{AGENT_HOOK_URL}{path}",
        json=payload,
        headers={"X-Agent-Token": AGENT_HOOK_TOKEN},
        timeout=15,
    )
    try:
        return r.json()
    except ValueError:
        return {"text": f"Agente: HTTP {r.status_code}"}


async def _forward(path: str, payload: dict) -> dict:
    if not AGENT_HOOK_TOKEN:
        return {"text": "AGENT_HOOK_TOKEN non configurato"}
    try:
        return await asyncio.get_running_loop().run_in_executor(None, _post, path, payload)
    except requests.RequestException as e:
        logging.error(f"agent hook {path}: {e}")
        return {"text": "Agente non raggiungibile"}


@events.register(events.CallbackQuery(pattern=rb"^agent:"))
async def callback(event: events.CallbackQuery.Event):
    if event.sender_id not in Utils.WHITELIST_IDS:
        await event.answer("Non autorizzato", alert=True)
        return
    res = await _forward(
        "/telegram/callback",
        {
            "data": event.data.decode(),
            "chat_id": event.chat_id,
            "user_id": event.sender_id,
            "message_id": event.message_id,
        },
    )
    await event.answer(str(res.get("text") or "OK")[:190])


@events.register(events.NewMessage(func=lambda e: e.is_reply and e.is_private))
async def reply(event: events.NewMessage.Event):
    if event.sender_id not in Utils.WHITELIST_IDS or not event.raw_text:
        return
    res = await _forward(
        "/telegram/reply",
        {
            "chat_id": event.chat_id,
            "user_id": event.sender_id,
            "reply_to_message_id": event.reply_to_msg_id,
            "text": event.raw_text,
        },
    )
    if res.get("handled") and res.get("message"):
        await event.reply(res["message"])
