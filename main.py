import requests
from bs4 import BeautifulSoup
import sqlite3
from fpdf import FPDF
from os import path

con = sqlite3.connect('saveInfo.db')
cur = con.cursor()
cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='saveInfo' ''')
if cur.fetchone()[0]==1 : 
    print('Table exists.')
else:
    print('Table does not exist.')
    cur.execute('''CREATE TABLE saveInfo(playerName text, playerCountry text, playerTeam text, acs real, kd real, kast real, adr real)''')
con.close()

def findRoles(playerAgents):
    duelist = ["jett", "pheonix", "reyna", "raze", "yoru", "neon"]
    controller = ["brimstone", "viper", "omen", "astra"]
    sentinel = ["killjoy", "cypher", "sage", "chamber"]
    initiator = ["sova", "breach", "skye", "kayo"]
    #roles = ["duelist", "controller", "sentinel", "initiator"]
    listOfRoles = []

    for agent in duelist:
        if agent in playerAgents:
            listOfRoles.append('duelist')
    
    for agent in controller:
        if agent in playerAgents:
            listOfRoles.append('controller')
    
    for agent in sentinel:
        if agent in playerAgents:
            listOfRoles.append('sentinel')
    
    for agent in initiator:
        if agent in playerAgents:
            listOfRoles.append('initiator')
    return listOfRoles


def insertVaribleIntoTable(playerName, country, team, acs, kd, kast, adr):  #function to add vlr info to sqlite database
    con = sqlite3.connect('saveInfo.db')
    cur = con.cursor()
    sqlite_insert_with_param = """INSERT INTO saveInfo
                          (playerName, playerCountry, playerTeam, acs, kd, kast, adr) 
                          VALUES (?, ?, ?, ?, ?, ?, ?);"""
    data_tuple = (playerName, country, team, acs, kd, kast, adr)
    cur.execute(sqlite_insert_with_param, data_tuple)
    con.commit()
    con.close()

def intoPDF(playerName, country, team, acs, kd, kast, adr, count, listOfRoles):  #function to turn stats to player cards
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()

    pdf.set_font('helvetica', 'B', 40)
    pdf.set_text_color(255,255,255)
    pdf.image('./bg.png', x = 0, y = 0, w = 210, h = 297)

    #input statistics
    x1= 19
    y1 = 187
    x2 = 19
    y2 = 214
    x3 = 19
    y3 = 242
    x4 = 19
    y4 = 270
    txt1 = kd
    txt2 = acs
    txt3 = kast
    txt4 = adr
    pdf.text(x1, y1, txt1)
    pdf.text(x2, y2, txt2)
    pdf.text(x3, y3, txt3)
    pdf.text(x4, y4, txt4)

    pdf.set_font('helvetica', 'B', 25)
    x= 15
    y = 20
    for role in listOfRoles:
        pdf.text(x, y, role.upper())
        y += 8

    #input info
    if path.exists("./flags/{}.png".format(country)):
        pass
        print("Flag exists!")
    else:
        response = requests.get("https://flagcdn.com/w320/{}.png".format(country))
        file = open("./flags/{}.png".format(country), "wb")
        file.write(response.content)
        file.close()
    pdf.image('./flags/{}.png'.format(country),37,100,18)
    txt5 = country.upper()
    txt6 = team
    if team is None:
        txt6 = "F/A"
    txt7 = playerName
    x5= 15
    y5 = 110
    x6 = 15
    y6 = 128
    x7 = 15
    y7 = 151
    pdf.set_font('helvetica', 'B', 40)
    pdf.text(x5, y5, txt5)
    pdf.set_font('helvetica', 'B', 60)
    pdf.text(x6, y6, txt6)
    pdf.set_font('helvetica', 'B', 80)
    pdf.text(x7, y7, txt7)

    pdf.output('playerCard{}.pdf'.format(count))
    print("Player Car Printed!")

region = "na"   #change this to na,eu,all,ap etc for different region specific lists

URL = "https://www.vlr.gg/stats/?event_group_id=all&event_id=all&region={}&country=all&min_rounds=200&min_rating=1550&agent=all&map_id=all&timespan=60d".format(region)
#alternatively change the parameters in this url to get other specific lists
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(id="wrapper")
mainTable = results.find("tbody")
collectionOfRows = mainTable.find_all("tr")

for count, row in enumerate(collectionOfRows):
    playerNameDiv = row.find_all("div", class_ = "text-of")
    playerName = playerNameDiv[0].string
    countryDiv = row.find_all('i')
    countryLine = str(countryDiv[0])
    country = countryLine[19:21]
    teamDiv = row.find_all("div", class_ = "stats-player-country")
    team = teamDiv[0].string
    kdDiv = row.find_all("div", class_ = "color-sq")
    acs = kdDiv[0].string
    kd = kdDiv[1].string
    kast = kdDiv[2].string
    adr = kdDiv[3].string
    playerAgents = row.find_all("td", class_ = "mod-agents")[0]
    playerAgents = str(playerAgents)
    listOfRoles = findRoles(playerAgents)
    insertVaribleIntoTable(playerName, country, team, acs, kd, kast, adr)
    if playerName == "leaf":       #change player name to make a playercard, you can add multiple names using or operator
        intoPDF(playerName, country, team, acs, kd, kast, adr, count, listOfRoles)   #you can hit CTRL+C when "Player Card Printed!" shows up
        break