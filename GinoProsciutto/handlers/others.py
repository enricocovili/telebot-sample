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
    # LEGACY / DEPRECATED
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

@events.register(events.NewMessage(pattern="/artiglio"))
async def artiglio(event: events.newmessage.NewMessage.Event):
    logging.info("received: artiglio")
    res = requests.get(Utils.artiglio_ranking_url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    ranking = soup.select("table")[0]
    matches = soup.select("table")[1]
    for row in ranking.select("tr"):
        cols = row.select("td")
        if len(cols) == 0:
            continue
        if "artiglio" in cols[1].getText().lower():
            b_rank = cols[0].getText()
            b_points = cols[2].getText()
    last_match = ""
    # iterate over tr that have class "dispari" or "pari"
    for match in matches.select("tr"):
        if not "dispari" in match.get("class", []) and not "pari" in match.get("class", []):
            continue
        cols = match.select("td")
        if len(cols) == 0:
            continue
        week_day = cols[3].getText()
        date = cols[2].getText()
        if "artiglio" in cols[6].getText().lower():
            opponent = cols[5].getText()
            casa = False
        else:
            opponent = cols[6].getText()
            casa = True
        # check if (result) is empty
        if cols[8].getText() == "":
            next_match = {"date": week_day + " " + date, "opponent": opponent, "casa": casa}
            break
        else:
            last_match = {"date": week_day + " " + date, "opponent": opponent, "result": cols[8].next.getText(), "casa": casa}
        
    output = f"""
        Informazioni su **Artiglio**:
        ⬤ **Rank Girone B**: {b_rank}
        ⬤ **Rank Girone A**: {b_rank} TODO: fix
        ⬤ **Punti**: {b_points}
        ⬤ **Prossima partita**: 
            {next_match["date"]}
            vs {next_match["opponent"]} 
            ({'casa' if next_match["casa"] else 'ospiti'})
        ⬤ **Ultima partita**: 
            {last_match["date"]} 
            vs {last_match["opponent"]} 
            ({last_match["result"]}) ({'casa' if last_match["casa"] else 'ospiti'})
    """
    # strip trailing whitespaces for every line if start with "⬤"
    output = "\n".join([line.strip() if line.strip().startswith("⬤") else line for line in output.split("\n")])
    # also cap every line starting with whitespaces to a max of 4 trailing whitespaces
    output = "\n".join([4*" " + line.strip() if line.startswith(" ") else line for line in output.split("\n")])
    await event.reply(output)