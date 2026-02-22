import asyncio
import os
import logging

from utils import Utils
from telethon import events


@events.register(events.NewMessage(pattern="/start_minecraft_server"))
async def start_minecraft_server(event: events.newmessage.NewMessage):
    if event.chat_id not in Utils.MINECRAFT_WHITELIST_IDS:
        await event.reply("❌ You are not allowed to use this command ❌")
        return
    
    # i need permissions to execute the command. i'm copying the first id in the whitelist 
    # and using it to execute the command

    fake_privileged_chat_id = Utils.WHITELIST_IDS[0]

    bot = event.client
    msg = await bot.send_message(event.chat_id, "⏳ Starting Minecraft server...")

    mac = os.getenv("MINECRAFT_SERVER_MAC")
    host = os.getenv("MINECRAFT_SERVER_HOST")
    user = os.getenv("MINECRAFT_SERVER_USERNAME")
    password = os.getenv("MINECRAFT_SERVER_PASSWORD")

    wake_on_lan_output = await Utils._exec(fake_privileged_chat_id, ["wakeonlan", mac])
    logging.debug(f"Wake-on-LAN output: {wake_on_lan_output}")
    await msg.edit("⏳ Wake-on-LAN sent, waiting for host to come online...")

    for attempt in range(5):
        await msg.edit(f"⏳ Host is still offline, attempt {attempt + 1}/5...")
        result = await Utils._exec(fake_privileged_chat_id, ["ping", "-c", "1", host])
        if "1 received" in result:
            break
        await asyncio.sleep(10)
    else:
        await msg.edit("❌ Host failed to come online after 10 attempts")
        return

    await msg.edit("✅ Host is online! Starting server... ⏳")
    start_command = await Utils._exec(
        fake_privileged_chat_id,
        f"sshpass -p {password} ssh -o StrictHostKeyChecking=no -l {user} {host}".split(
            " "
        )
        + ["'D: && cd Servers\\S_Mine && .\\mcserver.exe start'"],
    )
    logging.debug(f"Start command output: {start_command}")
    if "has already started" in start_command:
        await msg.edit("✅ Minecraft server is already running!")
        return
    await asyncio.sleep(10)
    await msg.edit("✅ Minecraft server started!")


@events.register(events.NewMessage(pattern="/stop_minecraft_server"))
async def stop_minecraft_server(event: events.newmessage.NewMessage):
    if event.chat_id not in Utils.MINECRAFT_WHITELIST_IDS:
        await event.reply("❌ You are not allowed to use this command ❌")
        return
    
    # i need permissions to execute the command. i'm copying the first id in the whitelist 
    # and using it to execute the command

    fake_privileged_chat_id = Utils.WHITELIST_IDS[0]

    bot = event.client
    msg = await bot.send_message(event.chat_id, "⏳ Stopping Minecraft server...")

    host = os.getenv("MINECRAFT_SERVER_HOST")
    user = os.getenv("MINECRAFT_SERVER_USERNAME")
    password = os.getenv("MINECRAFT_SERVER_PASSWORD")

    output = await Utils._exec(
        fake_privileged_chat_id,
        f"sshpass -p {password} ssh -o StrictHostKeyChecking=no -l {user} {host}".split(
            " "
        )
        + [f"'D: && cd Servers\\S_Mine && .\\mccron\mcrcon.exe -p {password} stop'"],
    )
    logging.debug(f"Stop command output: {output}")
    if "Connection failed" in output:
        await msg.edit("✅ Minecraft server is already stopped!")
        return
    await asyncio.sleep(3)
    await msg.edit("✅ Minecraft server stopped!")
