import datetime
from discord import Intents, Embed, Color
from discord.ext import commands
from scipy.optimize import linear_sum_assignment
import numpy as np

def int_to_month(m):
    res = ""
    match m:
        case 1:
            res = "janvier"
        case 2:
            res = "février"
        case 3:
            res = "mars"
        case 4:
            res = "avril"
        case 5:
            res = "mai"
        case 6:
            res = "juin"
        case 7:
            res = "juillet"
        case 8:
            res = "août"
        case 9:
            res = "septembre"
        case 10:
            res = "octobre"
        case 11:
            res = "novembre"
        case 12:
            res = "décembre"
    return res

def parse_msg(msg):
    preferences = {}
    prefs_list = msg.split("\n")[1:]
    for line in prefs_list:
        name, prefs = line.split(":")
        preferences[name.strip()] = [int(p) for p in prefs.strip().split("-")]
    return preferences

def affectation(preferences):
    nb_targets = 15
    nb_players = len(preferences)

    cost_matrix = np.full((nb_players, nb_targets), np.inf)
    for i, (player, prefs) in enumerate(preferences.items()):
        for index, target in enumerate(prefs):
            cost_matrix[i, target - 1] = index

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    total_cost = 0
    assignments = {}
    for i, player in enumerate(preferences.keys()):
        assignments[player] = col_ind[i] + 1
        if assignments[player] in preferences[player]:
            total_cost += preferences[player].index(assignments[player]) + 1
        else:
            total_cost += float('inf')

    return assignments, total_cost

def add_missing(assignments):
    missing = []
    res = {val: key for key, val in assignments.items()}
    for i in range(1, 16):
        if i not in res:
            missing.append(i)
    for m in missing:
        res[m] = "Non réservé"
    return res

#
# Bot setup
#
intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("Bot is ready...")

@bot.command()
async def assign_target(ctx, day:int):
    dt = datetime.date.today()
    title = f"Ligue {int_to_month(dt.month)} {dt.year}"
    description = f"Affectation des cibles du jour {day}"
    
    preferences = parse_msg(ctx.message.content)
    try:
        tmp_assignments,total_cost = affectation(preferences)
    except ValueError:
        await ctx.send("Pas de solution possibles. Il faut fournir plus de choix...")

    assignments = add_missing(tmp_assignments)

    embed = Embed(title=title, description=description)
    
    for key, val in dict(sorted(assignments.items())).items():
        if val == "Non réservé":
            name = f"__Village {key}__ : {val}"
        else:
            name =  f"__Village {key}__ : {val} - choix : {preferences[val].index(tmp_assignments[val]) + 1}"
        embed.add_field(name=name, value="", inline=False)
    
    embed.set_footer(text=f"{total_cost}")
    await ctx.send(embed=embed)



