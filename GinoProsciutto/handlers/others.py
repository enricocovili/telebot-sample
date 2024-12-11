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
    # send a nice formatted message using html. the row with "artiglio" is bold
    headers = ["Rank", "Nome", "Punti", "Giocate"]
    # get longest string for each column
    max_len = [len(header) for header in headers] # placeholders
    out = "<pre>"
    for row in rows:
        cols = row.select("td")
        if len(cols) == 0:
            continue
        cols = cols[0:4]
        for i, col in enumerate(cols):
            if len(col.getText()) > max_len[i]:
                max_len[i] = len(col.getText())
    out += "⎡" + "|".join(["⎺"*max_l for max_l in max_len]) + "⎤\n"
    out += "⎢" + "|".join(header.ljust(max_len[i]) for i, header in enumerate(headers)) + "|\n"
    out += "⎢" + "|".join(["-"*max_l for max_l in max_len]) + "⎥\n"
    for row in rows:
        cols = row.select("td")
        if len(cols) == 0:
            continue
        cols = cols[0:4]
        if "artiglio" in cols[1].getText().lower():
            out += "<b>"
        out += "⎢" + "|".join(col.getText().ljust(max_len[i]) for i, col in enumerate(cols)) + "|\n"
        if "artiglio" in cols[1].getText().lower():
            out += "</b>"
    out += "⎣" + "|".join(["_"*max_l for max_l in max_len]) + "⎦\n"
    out += "</pre>"
    await event.reply(out[:4000], parse_mode="html")
    # await event.reply(out[:4000], parse_mode="html")