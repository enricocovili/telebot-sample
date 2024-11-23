from utils import Utils
from telethon import events
import logging
import requests, bs4

@events.register(events.NewMessage(pattern="/exec"))
async def exec(event: events.newmessage.NewMessage.Event):
    msg = event.text.split()[1:]
    logging.info("received: exec " + " ".join(msg))
    out = await Utils._exec(event.chat_id, cmd=msg)
    await event.reply(out[:4000])

@events.register(events.NewMessage(pattern="/classifica_artiglio"))
async def classifica_artiglio(event: events.newmessage.NewMessage.Event):
    logging.info("received: classifica_artiglio")
    res = requests.get(Utils.artiglio_ranking_url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    table = soup.select("table")[0]
    rows = table.select("tr")
    classifica = []
    for row in rows[1:]:
        cells = row.select("td")
        classifica.append([cell.text.strip() for cell in cells])
    out = "```"
    for pos, team in enumerate(classifica):
        out += f"{pos+1}. {team[1]} - {team[2]} - {team[3]}\n"
    out += "```"
    await event.reply(out[:4000])