from telethon import events, Button
from utils import Utils


@events.register(events.NewMessage(pattern="/pistatus"))
async def pistatus(event: events.newmessage.NewMessage.Event):
    bot = event.client
    chat_id = event.chat.id
    output = ""
    for i in Utils.status_commands:
        for key, value in i.items():
            if key == "🌡️ temp":
                # also with "🌡️ temp" part
                raw_temp = await Utils._exec(chat_id, cmd=value, name=key)
                output += Utils.get_temperature(raw_temp)
            else:
                output += await Utils._exec(chat_id, cmd=value, name=key)
    await bot.send_message(event.chat, message=output[:4000])


@events.register(events.CallbackQuery)
async def callback(event):
    if event.data == b"reload_usb":
        output = await Utils._exec(event.chat.id, ["sudo", "mount", "-a"])
        if output == "":
            return await event.answer("USB DEVICES RELOADED")
        bot = event.client
        return await bot.send_message(event.chat, message=output[:4000])
    if event.data == b"general_status":
        await pistatus(event)
        return await event.answer()
    if event.data == b"close_menu":
        return await event.delete()


@events.register(events.NewMessage(pattern="/menu"))
async def menu(event: events.newmessage.NewMessage):
    # chat = await event.get_chat()
    bot = event.client
    await bot.send_message(
        event.chat,
        message="Select one of the options below:",
        buttons=[
            [
                Button.inline("🔃 Reload USB devices 🔃", data=b"reload_usb"),
                Button.inline(
                    "🔍 Info about RasPi status 🔍", data=b"general_status"
                ),
            ],
            [Button.inline("❌ Close Menu ❌", data=b"close_menu")],
        ],
    )
