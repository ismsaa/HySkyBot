from msilib.schema import IsolatedComponent
import numpy as np
import pandas as pd
import requests
import json
from openpyxl import load_workbook

def Import_Auctions():
    response_API = requests.get('https://api.hypixel.net/skyblock/auctions')
    data = response_API.text
    parse_json = json.loads(data)

    Pages = (int((parse_json["totalAuctions"])/1000))+1

    Auctions = pd.DataFrame(parse_json["auctions"])

    for i in range(1,Pages):
        response_API = requests.get('https://api.hypixel.net/skyblock/auctions?page='+str(i))
        #print(response_API.status_code)
        data = response_API.text
        parse_json = json.loads(data)
        AuctionsData = pd.DataFrame(parse_json["auctions"])
        Auctions = pd.concat([Auctions,AuctionsData], ignore_index=True)
    return Auctions

def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    return 0.0

def get_Flips(minPrice,maxPrice,priceDiff,minAmt):
    firstPrefixes = ["Very ","Highly ","Extremely ","Not So ","Thicc ","Absolutely ","Even More ","Robust ","Zooming ","Pleasant's ","Green Thumb ","Moil ","Toil ","Heroic ","Spicy ","Legendary ","Sharp ","Fabled ","Mythic ","Fierce ","Clean ","Smart ","Necrotic ","Titanic ","Pure ","Epic ","Forceful ","Reinforced ","Fine ","Salty ","Gentle ","Spiked ","Lush ","Precise ","Loving ","Light ","Jaded ","Hyper ","Shiny ","Excellent ","Rapid ","Fast ","Strengthened ","Grand ","Sturdy ","Shaded ","Treacherous ","Dirty ","Rich ","Glistening ","Withered ","Suspicious ","Deadly ","Great ","Fair ","Lucky ","Heated ","Blessed ","Bountiful ","Lumberjack's ","Double-Bit ","Rugged ","Stellar ","Magnetic ","Fleet ","Auspicious ","Ambered ","Unyielding ","Prospector's ","Fortunate ","Chomp ","Stiff ","Fortified ","Waxed ","Glistening ","Loving ","Ridiculous ","Cubic ","Empowered ","Renowned ","Submerged ","Candied ","Headstrong ","Spritual ","Neat ","Hasty ","Awkward ","Jerry's ","Bulky ","Warped ","Odd ","Bloody ","Fruitful ","Unreal ","Spiritual ","Gilded ","Demonic "]
    secondPrefixes = ["Heavy ","Wise ","Strong ","Giant ","Perfect ","Ancient ","Refined ","Undead "]
    #uniquePrefixes = ["Extremely ","Very ","Highly ","Not So ", "Absolutely ","Even More ","Thicc "]
    filterItems = ["Heavy Helmet","Heavy Chestplate","Heavy Leggings","Heavy Boots","Wise Dragon ","Strong Dragon ","Superior Dragon ", "Giant Cleaver","Ancient Cloak","Ancient Rose","Refined Mithril Pickaxe","Refined Titanium Pickaxe","Undead Bow","Undead Sword","Shiny Rod"]
    filterNames = ["Rune"," Cake","Skin","Tier ","Crab Hat ","Travel Scroll ","Enchanted Book"]
    
    priceDiff = priceDiff/100
    if maxPrice == 0:
        maxPrice = 10000000000000

    FilteredAuctions = Import_Auctions()

    FilteredAuctions = FilteredAuctions.loc[FilteredAuctions["bin"] == True].sort_values(['starting_bid'])
    FilteredAuctions = FilteredAuctions[['uuid','item_name','starting_bid']]

    TempFilterAucs = pd.DataFrame()

    FilteredAuctions['item_name'] = FilteredAuctions['item_name'].str.replace(' ✪', '').str.replace('✪', '').str.replace(' ✦', '').str.replace('✦', '').str.replace('➊', '').str.replace('➋', '').str.replace('✿ ', '').str.replace('➌', '').str.replace('⚚ ', '')

    for i in firstPrefixes:
        FilteredAuctions['item_name'] = FilteredAuctions['item_name'].str.replace(i, '')

    for l in range(1,101):
        FilteredAuctions['item_name'] = FilteredAuctions['item_name'].str.replace('\[Lvl '+str(l)+'] ', '', regex=True)


    for i in filterNames:
        FilteredAuctions = FilteredAuctions.loc[~FilteredAuctions["item_name"].str.contains(i)]

    for i in filterItems:
        TempFilterAuc = FilteredAuctions.loc[FilteredAuctions["item_name"].str.contains(i)]
        FilteredAuctions = FilteredAuctions.loc[~FilteredAuctions["item_name"].str.contains(i)]
        TempFilterAucs = pd.concat([TempFilterAucs,TempFilterAuc], ignore_index=True)

    for i in secondPrefixes:
        FilteredAuctions['item_name'] = FilteredAuctions['item_name'].str.replace(i, '')

    #for i in uniquePrefixes:
    #    TempFilterAucs['item_name'] = TempFilterAucs['item_name'].str.replace(i, '')


    FilteredAuctions = pd.concat([FilteredAuctions,TempFilterAucs], ignore_index=True)

    #FilteredAuctionsV2 = pd.DataFrame()
    tempSeries = pd.Series(dtype='float64')

    item_name_col = FilteredAuctions.columns.get_loc("item_name")
    starting_bid_col = FilteredAuctions.columns.get_loc("starting_bid")
    #print(item_name_col)
    #print(starting_bid_col)

    for row in FilteredAuctions.sort_values('starting_bid', ignore_index=True).groupby(['item_name']).head(1).itertuples():
        tempAucs = FilteredAuctions.loc[FilteredAuctions["item_name"] == row[item_name_col+1]].head(minAmt)
        if tempAucs.shape[0] < minAmt or (((tempAucs.iloc[1,starting_bid_col])*(1-priceDiff)) < ((tempAucs.iloc[0,starting_bid_col]))):
            FilteredAuctions = FilteredAuctions.loc[FilteredAuctions['item_name'] != tempAucs.iloc[0,item_name_col]]
        elif (((tempAucs.iloc[1,starting_bid_col])*(1-priceDiff)) >= ((tempAucs.iloc[0,starting_bid_col]))):
            firstItem = tempAucs.iloc[0,starting_bid_col]
            secondItem = tempAucs.iloc[1,starting_bid_col]
            percentProfit = pd.Series([round((secondItem/firstItem*100)-100,2)])
            #tempSeries = tempSeries.append(percentProfit)
            if firstItem > minPrice and firstItem < maxPrice:
                tempSeries = pd.concat([tempSeries,percentProfit], ignore_index=True)
            #FilteredAuctionsV2 = pd.concat([FilteredAuctionsV2,FilteredAuctions.loc[FilteredAuctions['item_name'] == tempAucs.iloc[0,0]]], ignore_index=True)
        
    #FilteredAuctions = FilteredAuctionsV2.copy()

    #print(tempSeries)

    FilteredAuctions = FilteredAuctions.groupby(['item_name']).head(1).loc[FilteredAuctions["starting_bid"] >= minPrice].loc[FilteredAuctions["starting_bid"] <= maxPrice]

    # Separated Version of line above
    # FilteredAuctions = FilteredAuctions.groupby(['item_name']).head(1)
    # FilteredAuctions = FilteredAuctions.loc[FilteredAuctions["starting_bid"] > minPrice]
    # FilteredAuctions = FilteredAuctions.loc[FilteredAuctions["starting_bid"] < maxPrice]

    #FilteredAuctions = FilteredAuctions.query("item_name == @item")

    #Sorting The Auctions
    FilteredAuctions = FilteredAuctions.sort_values('starting_bid', ignore_index=True)

    #FilteredAuctions["Percent_Diff"] = tempSeries
    FilteredAuctions = FilteredAuctions.assign(Percent_Profit = tempSeries)

    FilteredAuctions = FilteredAuctions[~FilteredAuctions['Percent_Profit'].isnull()]
    

    return FilteredAuctions