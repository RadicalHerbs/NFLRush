# Visually Representing NFL Game Data Snapshots at Handoff
# Charles Baird

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np
import csv
import os
import pandas as pd
import math

# Primary and Secondary Colors Dictionaries

pri_col = {
    "ARI": "#97233F",
    "ATL": "#A71930",
    "BAL": "#241773",
    "BUF": "#00338D",
    "CAR": "#0085CA",
    "CHI": "#0B162A",
    "CIN": "#FB4F14",
    "CLE": "#311D00",
    "DAL": "#041E42",
    "DEN": "#FB4F14",
    "DET": "#0076B6",
    "GB": "#203731",
    "HOU": "#03202F",
    "IND": "#002C5F",
    "JAX": "#00677F",
    "KC": "#E31837",
    "LA": "#002D72",
    "LAC": "#002A5E",
    "LAR": "#002D72",
    "LV": "#000000",
    "MIA": "#008E97",
    "MIN": "#F42683",
    "NE": "#002244",
    "NO": "#D3BC8D",
    "NYG": "#0B2265",
    "NYJ": "#125740",
    "OAK": "#000000",
    "PHI": "#004C54",
    "PIT": "#FFB612",
    "SEA": "#002244",
    "SF": "#AA0000",
    "TB": "#D50A0A",
    "TEN": "#0C2340",
    "WAS": "#773141"
    }  

sec_col = {
    "ARI": "#000000",
    "ATL": "#000000",
    "BAL": "#000000",
    "BUF": "#C60C30",
    "CAR": "#101820",
    "CHI": "#C83803",
    "CIN": "#000000",
    "CLE": "#FF3C00",
    "DAL": "#869397",
    "DEN": "#002244",
    "DET": "#B0B7BC",
    "GB": "#FFB612",
    "HOU": "#A71930",
    "IND": "#A2AAAD",
    "JAX": "#D7A22A",
    "KC": "#FFB81C",
    "LA": "#FFCD00",
    "LAC": "#FFC20E",
    "LAR": "#FFCD00",
    "LV": "#A5ACAF",
    "MIA": "#FC4C02",
    "MIN": "#FFC62F",
    "NE": "#C8102E",
    "NO": "#101820",
    "NYG": "#A71930",
    "NYJ": "#000000",
    "OAK": "#A5ACAF",
    "PHI": "#A5ACAF",
    "PIT": "#101820",
    "SEA": "#69BE28",
    "SF": "#B3995D",
    "TB": "#FF7900",
    "TEN": "#4B92DB",
    "WAS": "#FFB612"
	}

games_grouped = pd.read_csv('train.csv', low_memory = False).groupby("GameId")

font_jersey = ImageFont.truetype("AldotheApache.ttf",12)
font_field = ImageFont.truetype("cebswfte.ttf",20)

def draw_field(lb, rb, play):
    img = Image.new("RGB", (int((rb - lb) * 10) ,530), "Green")
    ball_right = (play["PlayDirection"].iloc[0] == "right")
    opp_field = play["FieldPosition"].iloc[0] != play["PossessionTeam"].iloc[0]
    los = ((10 + play["YardLine"].iloc[0]) if (ball_right & (not opp_field)) | ((not ball_right) & opp_field)\
            else (110 - play["YardLine"].iloc[0])) - lb
    lines = ImageDraw.Draw(img)
    if(rb > 110):
        lines.rectangle([int((110 - lb) * 10), 0, int((rb - lb) * 10), 530], fill = pri_col.get(play["VisitorTeamAbbr"].iloc[0]))
    if(lb < 10):
        lines.rectangle([0, 0, int((10 - lb) * 10), 530], fill = pri_col.get(play["HomeTeamAbbr"].iloc[0]))
    lines.line((los * 10,0) + (los * 10, 530), fill = "Blue", width = 5)
    lines.line(((los + (-play["Distance"].iloc[0] if (not ball_right) else play["Distance"].iloc[0])) * 10, 0) +\
	((los + (-play["Distance"].iloc[0] if (not ball_right) else play["Distance"].iloc[0])) * 10, 530),\
        fill = "Yellow", width = 5)
    
    for i in range(int(lb), int(rb + 1)):
        if ((i >= 10) & (i <= 110)):
            lines.line(((i - lb) * 10, 0) + ((i - lb) * 10, 530 if (i % 5 == 0) else 10),\
                    fill = "White", width = (3 if ((i == 10) | (i == 110)) else 0))
            lines.line(((i - lb) * 10, 520) + ((i - lb) * 10, 530), fill = "White")
        if i % 10 == 0:
            lines.text(((i - lb - 1) * 10, 20), "" if ((i == 110) | (i == 10)) else (str(110 - i) if i > 50 else str(i - 10)),\
                    font = font_field)
            lines.text(((i - lb - 1) * 10, 510), "" if ((i == 110) | (i == 10)) else (str(110 - i) if i > 50 else str(i - 10)),\
                    font = font_field)
    return img

def get_team(row): 
    return row["HomeTeamAbbr"] if row["Team"] == "home" else row["VisitorTeamAbbr"] 

def add_player(row, lb, players):
    players.line([(row["X"] - math.sin(math.radians(row["Orientation"])) - lb) * 10,\
            (row["Y"] - math.cos(math.radians(row["Orientation"]))) * 10,\
            (row["X"] + math.sin(math.radians(row["Orientation"])) - lb) * 10,\
            (row["Y"] + math.cos(math.radians(row["Orientation"])))  * 10],\
            fill = pri_col.get(get_team(row)) if row["NflId"] != row["NflIdRusher"] else "#F79AC0")
    players.line([(row["X"] - math.cos(math.radians(row["Dir"]) * row["S"]) - lb) * 10,\
            (row["Y"] - math.sin(math.radians(row["Dir"])) * row["S"]) * 10,\
            (row["X"] - lb) * 10,\
            (row["Y"])  * 10],\
            fill = pri_col.get(get_team(row)) if row["NflId"] != row["NflIdRusher"] else "#F79AC0")
    
    players.polygon([(row["X"] - math.sin(math.radians(row["Orientation"])) - lb) * 10,\
            (row["Y"] - math.cos(math.radians(row["Orientation"]))) * 10,\
            (row["X"] + math.sin(math.radians(row["Orientation"])) - lb) * 10,\
            (row["Y"] + math.cos(math.radians(row["Orientation"])))  * 10,\
            (row["X"] + math.cos(math.radians(row["Dir"]) * row["Dis"] * 10) - lb) * 10,\
            (row["Y"] + math.sin(math.radians(row["Dir"])) * row["Dis"] * 10) * 10],\
            fill = pri_col.get(get_team(row)) if row["NflId"] != row["NflIdRusher"] else "#F79AC0",\
            outline = sec_col.get(get_team(row)) if row["NflId"] != row["NflIdRusher"] else "#F79AC0")

#    players.text(((row["X"] - lb)*10,row["Y"]*10),
#	str(row["JerseyNumber"]),
#	pri_col.get(get_team(row)) if row["NflId"] != row["NflIdRusher"]
#	else "#F79AC0",
#	font=font_jersey)

def visual_play(play):
    lb = min(play["X"]) - 5
    rb = max(play["X"]) + 5
    im = draw_field(lb, rb, play)
    players = ImageDraw.Draw(im)

    play.apply(add_player, axis = 1, lb = lb, players = players)

    if not os.path.exists(str(play["GameId"].iloc[0])):
        os.makedirs(str(play["GameId"].iloc[0]))
    im.save(str(play["GameId"].iloc[0]) + '/' + str(play["PlayId"].iloc[0]) + '.png')

def visual_all(game_by_play):
    for playid, play in game_by_play:
        visual_play(play)
for gameid, game in games_grouped:
    visual_all(game.groupby("PlayId"))
#game1_by_play = games_grouped.get_group(2017090700).groupby("PlayId")
#visual_all(game1_by_play)

## To run for every play for every game
#for gameid, game in games_grouped:
