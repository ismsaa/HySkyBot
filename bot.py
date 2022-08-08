import os
from Hypixel_Auctions_Functions import *
import discord
import random
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms
import threading
import pyperclip
import time
from numerize import numerize
import json
from tabulate import tabulate

def ReloadGUI(f_stop):
    global data
    global Auctions
    global minPrice
    global maxPrice
    global priceDiff
    global minAmt
    global updateTable
    global CHANNEL

    #current = time()
    minPrice = 1000000
    maxPrice = 0
    priceDiff = 20
    minAmt = 12
    Auctions = get_Flips(minPrice,maxPrice,priceDiff,minAmt)
    Auctions.drop(['uuid'],axis=1,inplace=True)
    Auctions['starting_bid'] = Auctions['starting_bid'].apply(lambda x: numerize.numerize(x))
    Auctions.reset_index(drop=True)
    #call(["python", "Flip_Hypixel_Auctions.py"])
    #Auctions = pd.read_parquet('Flip_Hypixel_Auctions.parquet', engine="fastparquet")
    #data = Auctions.values.tolist()

    fig, ax = plt.subplots()
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')
    #fig = plt.figure(figsize=(6,1))
    table = ax.table(cellText=Auctions.values, colLabels=Auctions.columns, loc='center', cellLoc = 'center')
    table.auto_set_font_size(False)
    table.set_fontsize(13.0)
    table.scale(2,2)
    #fig.tight_layout()

    #plt.axis('off')
    #plt.grid('off')
    plt.gcf().canvas.draw()
    # get bounding box of table
    points = table.get_window_extent(plt.gcf()._cachedRenderer).get_points()
    # add 10 pixel spacing
    points[0,:] -= 10; points[1,:] += 10
    # get new bounding box in inches
    nbbox = matplotlib.transforms.Bbox.from_extents(points/plt.gcf().dpi)
    # save and clip by new bounding box
    #plt.savefig(__file__+'test.png', bbox_inches=nbbox, )
    plt.savefig('Flip_Auctions.png', bbox_inches=nbbox, dpi = 100)

    if not f_stop.is_set():
        # call f() again in 2 seconds
        threading.Timer(1, ReloadGUI, [f_stop]).start()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_NAME = os.getenv('GUILD_NAME')
GUILD_ID = os.getenv('GUILD_ID')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')
CHANNEL_ID = os.getenv('CHANNEL_ID')


client = discord.Client()



updateTable = True
f_stop = threading.Event()

minPrice = 1000000
maxPrice = 0
priceDiff = 20
minAmt = 12
#Auctions = get_Flips(minPrice,maxPrice,priceDiff,minAmt)
#Auctions['starting_bid'] = Auctions['starting_bid'].apply(lambda x: numerize.numerize(x))
#data = Auctions.values.tolist()

@client.event
async def on_ready():
    global data
    global Auctions
    global updateTable
    GUILD = discord.utils.get(client.guilds, name=GUILD_NAME)
    #print(f'{GUILD.name}(id: {GUILD.id})')
    CHANNEL = discord.utils.get(GUILD.channels, name=CHANNEL_NAME)
    #print(CHANNEL)
    print(f'{client.user.name} has connected to Discord!')
    ReloadGUI(f_stop)
    while(True):
        if updateTable:
            #await CHANNEL.send(tabulate(Auctions, headers=['index','UUID','Item','Price','Profit']))
            await CHANNEL.send(file=discord.File('Flip_Auctions.png'))
            time.sleep(10)
    

    

@client.event
async def on_message(message):
    global CHANNEL
    global updateTable
    if message.author == client.user:
        return

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    if message.content == '99!':
        response = random.choice(brooklyn_99_quotes)
        await message.channel.send(response)
    if message.content == 'FLIP ON':
        updateTable = True
    if message.content == 'FLIP OFF':
        updateTable = False
        

client.run(TOKEN)