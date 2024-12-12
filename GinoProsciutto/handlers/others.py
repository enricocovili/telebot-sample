from utils import Utils
from telethon import events
import logging
import requests, bs4

"""
    Ranking row
    0. Rank
    1. Name
    2. Points
    3. Played
    4. Won
    5. Lost
    6. 3-0
    7. 3-1
    8. 3-2
    9. 2-3
    10. 1-3
    11. 0-3
    12. SW (Sets won)
    13. SS (Sets lost)
    14. QS (Set ratio)
    15. PS (Points won)
    16. PR (Points lost)
    17. QR (Points ratio)
    18. Pen (Penalties)
"""

class Team:
    def __init__(self, round, rank, name, points, played, won, lost, three_zero, three_one, three_two, two_three, one_three, zero_three, sets_won, sets_lost, set_ratio, points_won, points_lost, points_ratio, penalties):
        self.round = round
        self.local_rank = int(rank)
        self.name = name
        self.points = int(points)
        self.played = int(played)
        self.won = int(won)
        self.lost = int(lost)
        self.three_zero = int(three_zero)
        self.three_one = int(three_one)
        self.three_two = int(three_two)
        self.two_three = int(two_three)
        self.one_three = int(one_three)
        self.zero_three = int(zero_three)
        self.sets_won = int(sets_won)
        self.sets_lost = int(sets_lost)
        self.set_ratio = float(set_ratio.replace(",", "."))
        self.points_won = int(points_won)
        self.points_lost = int(points_lost)
        self.points_ratio = float(points_ratio.replace(",", "."))
        self.penalties = int(penalties)
        self.global_rank = -1

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.round} | {self.name}"

"""
    Match row
    0. Skip
    1. Code
    2. Date
    3. Week day
    4. Time
    5. Home team
    6. Away team
    7. Skip
    8. Result
    9. Skip
"""

class Match:
    def __init__(self, __a, code, date, week_day, time, home_team, away_team, __b, result, __c):
        self.code = code
        self.date = date
        self.week_day = week_day
        self.time = time
        self.home_team = home_team
        self.away_team = away_team
        self.result = result

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

    def __repr__(self):
        return f"{self.home_team} vs {self.away_team}"

def load_teams(url: str):
    teams = []
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    table = soup.select("table")[0]
    rows = table.select("tr")
    for row in rows:
        cols = row.select("td")
        if len(cols) == 0:
            continue
        team = Team("A" if "girone=A" in url else "B", *[col.getText() for col in cols])
        teams.append(team)
    return teams

def get_full_ranks():
    teams = load_teams(Utils.artiglio_ranking_url)
    teams = teams + load_teams(Utils.artiglio_ranking_url.split("girone=B")[0] + "girone=A")
    # sort the teams based on (order is important): points, number of wins, QS, QP
    teams.sort(key=lambda x: (x.points, x.won, x.set_ratio, x.points_ratio), reverse=True)
    for i, team in enumerate(teams):
        team.global_rank = i + 1
    return teams

def get_matches():
    res = requests.get(Utils.artiglio_ranking_url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    matches = []
    for match in soup.select("table")[1].select("tr"):
        if not "dispari" in match.get("class", []) and not "pari" in match.get("class", []):
            continue
        cols = match.select("td")
        if len(cols) == 0:
            continue
        matches.append(Match(*[col.getText() for col in cols]))
        matches[-1].result = matches[-1].result[0:5]
    return matches

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
    teams = get_full_ranks()
    matches = get_matches()
    
    info_artiglio = [team for team in teams if "artiglio" in team.name.lower()][0]

    last_match = Match("", "", "", "", "", "", "", "", "", "")
    next_match = Match("", "", "", "", "", "", "", "", "", "")

    for ix, match in enumerate(matches[:-1]):
        if matches[ix+1].result == "":
            last_match = match
            next_match = matches[ix+1]
            break
    
    # Mobile friendly output
    output = f"""
        Informazioni su **Artiglio**:
        ⬤ **Rank Girone {info_artiglio.round}**: {info_artiglio.local_rank}
        ⬤ **Rank Generale**: {info_artiglio.global_rank}
        ⬤ **Punti**: {info_artiglio.points}
        ⬤ **% Vittorie**: {round(info_artiglio.won / info_artiglio.played * 100, 2)}% ({info_artiglio.won}/{info_artiglio.played})
        ⬤ **Prossima partita**:
            {next_match.week_day + ' ' + next_match.date + ' ' + next_match.time}
            vs {next_match.away_team if 'artiglio' in next_match.home_team.lower() else next_match.home_team} 
            ({'casa' if 'artiglio' in next_match.home_team.lower() else 'ospiti'})
        ⬤ **Ultima partita**: 
            {last_match.week_day + ' ' + last_match.date + ' ' + last_match.time}
            vs {last_match.away_team if 'artiglio' in last_match.home_team.lower() else last_match.home_team}
            ({last_match.result}) ({'casa' if 'artiglio' in last_match.home_team.lower() else 'ospiti'})
    """
    # All this shit is needed because i use multiline strings. I know there are better methods, i simply don't care
    # strip trailing whitespaces for every line if start with "⬤"
    output = "\n".join([line.strip() if line.strip().startswith("⬤") else line for line in output.split("\n")])
    # also cap every line starting with whitespaces to a max of 4 trailing whitespaces
    output = "\n".join([4*" " + line.strip() if line.startswith(" ") else line for line in output.split("\n")])
    await event.reply(output)