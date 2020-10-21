#!/usr/bin/env python3
import discord, discord.utils, random, os, re, json, sys, time, secrets, pyodbc
from os import path
from datetime import datetime, timedelta
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

from rulewordings import throwrules, slamrules

directory = os.path.dirname(os.path.realpath(__file__))

load_dotenv()
key = os.getenv('DISCORD_KEY')
status = os.getenv('DISCORD_STATUS')

SQLServer = os.getenv('SQL_SERVER')
SQLDatabase = os.getenv('SQL_DATABASE')
SQLLogin = os.getenv('SQL_LOGIN')
SQLPassword = os.getenv('SQL_PASSWORD')

SQLConnString = 'Driver={ODBC Driver 17 for SQL Server};Server=' + SQLServer+ ';Database=' + SQLDatabase + ';UID='+ SQLLogin +';PWD=' + SQLPassword

sqlConn = pyodbc.connect(SQLConnString)

#cursor = sqlConn.cursor()         
#cursor.execute('SELECT * FROM sys.databases')
#for row in cursor:
#    print(row)

#Bad way to do it, I know.
colours = ["default","teal","dark teal","green","dark green","blue","dark blue","purple","dark purple","magenta","dark magenta","gold","dark gold","orange","dark orange","red","dark red","lighter grey", "dark grey", "light grey", "darker grey", "blurple", "greyple"]
colourings = {"default":discord.Colour.default(),"teal":discord.Colour.teal(),"dark teal":discord.Colour.dark_teal(),"green":discord.Colour.green(),"dark green":discord.Colour.dark_green(),"blue":discord.Colour.blue(),"dark blue":discord.Colour.dark_blue(),"purple":discord.Colour.purple(),"dark purple":discord.Colour.dark_purple(),"magenta":discord.Colour.magenta(),"dark magenta":discord.Colour.dark_magenta(),"gold":discord.Colour.gold(),"dark gold":discord.Colour.dark_gold(),"orange":discord.Colour.orange(),"dark orange":discord.Colour.dark_orange(),"red":discord.Colour.red(),"dark red":discord.Colour.dark_red(),"lighter grey":discord.Colour.lighter_grey(),"dark grey":discord.Colour.dark_grey(),"light grey":discord.Colour.light_grey(),"darker grey":discord.Colour.darker_grey(),"blurple":discord.Colour.blurple(),"greyple":discord.Colour.greyple()}

timezones = {"PST":{"Name":"Pacific Standard Time", "Offset":-8, "Hours":-8, "Minutes":0},"PDT":{"Name":"Pacific Daylight Time", "Offset":-7, "Hours":-8, "Minutes":0},
             "MST":{"Name":"Mountain Standard Time", "Offset":-7, "Hours":-7, "Minutes":0},"MDT":{"Name":"Mountain Daylight Time", "Offset":-6, "Hours":-6, "Minutes":0},
             "CST":{"Name":"Central Standard Time", "Offset":-6, "Hours":-6, "Minutes":0},"CDT":{"Name":"Central Daylight Time", "Offset":-5, "Hours":-5, "Minutes":0},
             "EST":{"Name":"Eastern Standard Time", "Offset":-5, "Hours":-5, "Minutes":0},"EDT":{"Name":"Eastern Daylight Time", "Offset":-4, "Hours":-4, "Minutes":0},
             "UTC":{"Name":"Universal Time Constant", "Offset":0, "Hours":0, "Minutes":0},
             "GMT":{"Name":"Greenwich Mean Time", "Offset":0, "Hours":0, "Minutes":0},"BST":{"Name":"British Summer Time", "Offset":1, "Hours":1, "Minutes":0},
             "CET":{"Name":"Central European Time", "Offset":1, "Hours":1, "Minutes":0},"CEST":{"Name":"Central Europe Summer Time", "Offset":2, "Hours":2, "Minutes":0},
             "EET":{"Name":"Eastern European Time", "Offset":2, "Hours":2, "Minutes":0},"EEST":{"Name":"Eastern Europe Summer Time", "Offset":3, "Hours":3, "Minutes":0},
             "WST":{"Name":"(Australian) Western Standard Time", "Offset":8, "Hours":8, "Minutes":0},
             "ACST":{"Name":"Australian Central Standard Time", "Offset":9.5, "Hours":9, "Minutes":30},"ACDT":{"Name":"Australian Central Daylight Saving Time", "Offset":10.5, "Hours":10, "Minutes":30},
             "AEST":{"Name":"Australian Eastern Standard Time", "Offset":10, "Hours":10, "Minutes":0},"AEDT":{"Name":"Australian Eastern Daylight Saving Time", "Offset":11, "Hours":11, "Minutes":0},
             "NZST":{"Name":"New Zealand Standard Time", "Offset":12, "Hours":12, "Minutes":0},"NZDT":{"Name":"New Zealand Daylight Time", "Offset":13, "Hours":13, "Minutes":0}}

digitemojis = {1:"1️⃣",2:"2️⃣",3:"3️⃣",4:"4️⃣",5:"5️⃣",6:"6️⃣",7:"7️⃣",8:"8️⃣",9:"9️⃣",10:"🔟"}
emojidigits = {"1️⃣":1,"2️⃣":2,"3️⃣":3,"4️⃣":4,"5️⃣":5,"6️⃣":6,"7️⃣":7,"8️⃣":8,"9️⃣":9,"🔟":10}
             


client = discord.Client()

def randomcolour():
    colour = secrets.token_hex(3)
    return colour

def validatetz(tz):
    try:
        offset = timezones[tz]
        return True
    except:
        return False

def isowner(guild,user):
    if guild.owner == user:
        return True
    else:
        return False

def isadmin(guild,user):
    userRoles = user.roles
    roleParam = ""
    for role in userRoles:
        roleParam = "," + str(role.id)
    cursor = sqlConn.cursor()
    roleParam = roleParam[2:]
    cursor.execute('EXEC corgi.GetUserAccess ?, ?;',guild.id,roleParam)
    for row in cursor:
        if row[1] == "Server Administrator":
            cursor.close()
            return True
    cursor.close()
    return False

def isheadjudge(guild,user):
    userRoles = user.roles
    roleParam = ""
    for role in userRoles:
        roleParam = "," + str(role.id)
    cursor = sqlConn.cursor()
    roleParam = roleParam[2:]
    cursor.execute('EXEC corgi.GetUserAccess ?, ?;',guild.id,roleParam)
    for row in cursor:
        if row[1] == "Server Administrator":
            cursor.close()
            return True
    cursor.close()
    return False
def isjudge(guild,user):
    userRoles = user.roles
    roleParam = ""
    for role in userRoles:
        roleParam = "," + str(role.id)
    cursor = sqlConn.cursor()
    roleParam = roleParam[2:]
    cursor.execute('EXEC corgi.GetUserAccess ?, ?;',guild.id,roleParam)
    for row in cursor:
        if row[1] == "Judge" or row[1] == "Head Judge":
            cursor.close()
            return True
    cursor.close()
    return False

def iscaptain(guild,user):
    userRoles = user.roles
    roleParam = ""
    for role in userRoles:
        roleParam = "," + str(role.id)
    cursor = sqlConn.cursor()
    roleParam = roleParam[2:]
    cursor.execute('EXEC corgi.GetUserAccess ?, ?;',guild.id,roleParam)
    for row in cursor:
        if row[1] == "Team Captain":
            cursor.close()
            return True
    cursor.close()
    return False


async def germanpairing(message):
    #define checks
    def winnerResponse(r,u):
        return r.message.id == winner.id and u.id == message.author.id and r.emoji in ("✅","❎")
    def tableResponse(r,u):
        return r.message.id == table.id and u.id == winningPlayer.id and r.emoji in ("1️⃣","3️⃣")
    def winnerDm(m):
        return m.author.id == winningPlayer.id and m.channel.type == discord.ChannelType.private
    def loserDm(m):
        return m.author.id == losingPlayer.id and m.channel.type == discord.ChannelType.private

    #What emojis we got?
    greenTick = "✅"
    greenCross = "❎"
    oneDigit = "1️⃣"
    threeDigit = "3️⃣"

    #Who won the roll?
    response = "Did you win the dice roll, " + message.author.display_name + "?"
    winner = await message.channel.send(response.format(message))
    await winner.add_reaction(greenTick)
    await winner.add_reaction(greenCross)
    #Get that reaction
    try:
        reply = await client.wait_for('reaction_add',check=winnerResponse,timeout=10)
    except:
        response = "No response received. Pairing cancelled. If you have not yet rolled off, each use the `$roll` command."
        await message.channel.send(response.format(message))
        return
    
    #Set winner/loser based on reaction
    if reply[0].emoji == greenCross:
        response = "You lost the dice roll, " + message.mentions[0].display_name +" gets to choose the first table."
        winningPlayer = message.mentions[0]
        losingPlayer = message.author
    else:
        response = "You won the dice roll, you get to choose the first table."
        winningPlayer = message.author
        losingPlayer = message.mentions[0]
    await message.channel.send(response.format(message))

    #What table do you want, winner?
    response = winningPlayer.display_name + " what table would you like to place your first player card on?"
    table = await message.channel.send(response.format(message))
    await table.add_reaction(oneDigit)
    await table.add_reaction(threeDigit)
    #Get that reaction
    try:
        reply = await client.wait_for('reaction_add',check=tableResponse,timeout=180)
    except:
        response = "No response received. Pairing cancelled."
        await message.channel.send(response.format(message))
        return
    #Set table order for selection
    if reply[0].emoji == oneDigit:
        firstTable = oneDigit
        secondTable = threeDigit
    else:
        firstTable = threeDigit
        secondTable = oneDigit
    
    #Get Winning Player First Card
    response = winningPlayer.display_name + " has chosen to place their first card on table " + firstTable + ". Please reply to the DM to confirm the player, and casters, that will you will be placing on this table."
    await message.channel.send(response.format(message))
    dm = "Please respond with the Player Name, and their casters, that you would like to play on table " + firstTable + ". For example: Thom: Lucant and Aurora2"
    await winningPlayer.send(dm.format(message))
    try:
        winnerFirstPlayer = await client.wait_for('message',check=winnerDm,timeout=600)
    except:
        response = "No response received to DM. Pairing cancelled."
        await message.channel.send(response.format(message))
        return
    response = winningPlayer.display_name + " has chosen their first card. " + losingPlayer.display_name + " please reply to the DM to confirm the player, and casters, that will you will be placing on table " + secondTable + "."
    await message.channel.send(response.format(message))
    #Get Losing Player First Card
    dm = "Please respond with the Player Name, and their casters, that you would like to play on table " + secondTable + ". For example: Thom, Lucant and Aurora2"
    await losingPlayer.send(dm.format(message))
    try:
        loserFirstPlayer = await client.wait_for('message',check=loserDm,timeout=600)
    except:
        response = "No response received to DM. Pairing cancelled."
        await message.channel.send(response.format(message))
        return
    response = winningPlayer.display_name + " has chosen to play the following card on table " + firstTable + ": " + winnerFirstPlayer.content + "\n" + losingPlayer.display_name + " has chosen to play the following card on table " + secondTable + ": " + loserFirstPlayer.content
    await message.channel.send(response.format(message))
    response = winningPlayer.display_name + " please respond to the DM to confirm what card will be played on table " + secondTable + "."
    await message.channel.send(response.format(message))

    #Get Winning Player Second Card
    dm = "Please respond with the Player Name, and their casters, that you would like to play on table " + secondTable + ". This will be against the following card: " + loserFirstPlayer.content + ". For example: Ryan, Harbinger and Feora4"
    await winningPlayer.send(dm.format(message))
    try:
        winnerSecondPlayer = await client.wait_for('message',check=winnerDm,timeout=600)
    except:
        response = "No response received to DM. Pairing cancelled."
        await message.channel.send(response.format(message))
        return
    response = winningPlayer.display_name + " has chosen their second card. " + losingPlayer.display_name + " please reply to the DM to confirm the player, and casters, that will you will be placing on table " + firstTable + "."
    await message.channel.send(response.format(message))

    #Get Losing Player Second Card
    dm = "Please respond with the Player Name, and their casters, that you would like to play on table " + firstTable + ". This will be against the following card: " + winnerFirstPlayer.content + ".  For example: Ryan, Harbinger and Feora4"
    await losingPlayer.send(dm.format(message))
    try:
        loserSecondPlayer = await client.wait_for('message',check=loserDm,timeout=600)
    except:
        response = "No response received to DM. Pairing cancelled."
        await message.channel.send(response.format(message))
        return
    #We did it!!!
    opponents = "All player cards have been chosen!\n"
    #Tell people who they are playing
    if firstTable == oneDigit:
        opponents = opponents + "1️⃣: " + winnerFirstPlayer.content + " **VS** " + loserSecondPlayer.content + "\n2️⃣: Players that were not selected.\n3️⃣: " + winnerSecondPlayer.content + " **VS** " + loserFirstPlayer.content
    else:
        opponents = opponents + "1️⃣: " + winnerSecondPlayer.content + " **VS** " + loserFirstPlayer.content + "\n2️⃣: Players that were not selected.\n3️⃣: " + winnerFirstPlayer.content + " **VS** " + loserSecondPlayer.content
    await message.channel.send(opponents.format(message))
    return

async def addaccess(message,serverRoles):
    #Check permissions
    if isowner(message.guild,message.author) or isadmin(message.guild,message.author):
        #Open a connection
        cursor = sqlConn.cursor()
        #Get details of the role
        roleid = None
        if len(message.role_mentions) == 1:
            rolename = message.role_mentions[0].name
            roleid = message.role_mentions[0].id
        else:
            rolename = message.content[15:]
            for role in serverRoles:
                if role.name.lower() == rolename.lower():
                    roleid = role.id
                    rolename = role.name
                    break
        #There is no role
        if roleid is None:
            response = "Role not found, access level has not been changed."
            await message.channel.send(response.format(message))
        else:
            #Get role levels
            cursor.execute('EXEC corgi.GetAccessLevels;')
            r = 1
            response = "What access level would you like to the the role?"
            levels = []
            accesses = []
            for row in cursor:
                response = response + "\n" + digitemojis[r] + ": " + row[1]
                levels.append(row[0])
                accesses.append(row[1])
                r = r + 1
            cursor.close()
            rows = r - 1
            #prompt user and add reactions
            access = await message.channel.send(response.format(message))
            r = 1
            while r <= rows:
                await access.add_reaction(digitemojis[r])
                r = r + 1
            def accessResponse(r,u):
                return r.message.id == access.id and u.id == message.author.id and emojidigits[r.emoji] <= rows
            try:
                reply = await client.wait_for('reaction_add',check=accessResponse,timeout=10)
            except:
                #Got bored waiting
                response = "No response received. Access amendment cancelled."
                await message.channel.send(response.format(message))
                return
            #Add the access
            response = "Adding access level " + accesses[emojidigits[reply[0].emoji]-1] + " to role " + rolename + "."
            await message.channel.send(response.format(message))
            cursor.execute('EXEC corgi.AddRoleAccess ?, ?, ?;',message.guild.id,roleid,levels[emojidigits[reply[0].emoji]-1])
            sqlConn.commit()
            cursor.close()
    return

async def removeaccess(message):
    #Check permissions
    if isowner(message.guild,message.author) or isadmin(message.guild,message.author):
        #Get details of the role
        delrole = None
        if len(message.role_mentions) == 1:
            delrole = message.role_mentions[0]
        else:
            rolename = message.content[18:]
            serverRoles = message.guild.roles
            for role in serverRoles:
                if role.name.lower() == rolename.lower():
                    delrole = role
                    break
        ##There is no role
        if delrole is None:
            response = "Role not found, access level has not been changed."
            await message.channel.send(response.format(message))
        else:
            response = "Permissions related to the role " + delrole.name + " have been removed."
            await message.channel.send(response.format(message))
            await removeaccesslevel(message.guild,delrole)
    return

async def removeaccesslevel(guild,role):
    cursor = sqlConn.cursor()
    cursor.execute('EXEC corgi.RemoveRoleAccess ?, ?;',guild.id,role.id)
    sqlConn.commit()
    cursor.close()


async def checkaccess(message):
    if isowner(message.guild,message.author) or isadmin(message.guild,message.author):
        #Get details of the role
        checkrole = None
        if len(message.role_mentions) == 1:
            checkrole = message.role_mentions[0]
        else:
            rolename = message.content[17:]
            serverRoles = message.guild.roles
            for role in serverRoles:
                if role.name.lower() == rolename.lower():
                    checkrole = role
                    break
        ##There is no role
        if checkrole is None:
            response = "Role not found."
            await message.channel.send(response.format(message))
        else:
            cursor = sqlConn.cursor()
            cursor.execute('EXEC corgi.GetRoleAccess ?, ?;',message.guild.id,checkrole.id)
            response = None
            for row in cursor:
                response = "The role " + checkrole.name + " currently has the access level " + row[1] + "."
            cursor.close()
            if response is None:
                response = "The role " + checkrole.name + " currently has no access level."
            await message.channel.send(response.format(message))
    return



@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))
    game = discord.Game(status)
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print('Message from {0.author}: {0.content}'.format(message))

    if message.channel.type == discord.ChannelType.private:
        return

    serverRoles = message.guild.roles

    roles = message.author.roles
    isCommittee = False
    isCaptain = False
    isJudge = False
    isThom = False
    for role in roles:
        #As people, by design, can't have multiple rules, then we can safely break and not loop around 40~ roles
        if role.name == "Thom":
            isThom = True
        if role.name == "VTC Committee" or role.name == "Thom":
            isCommittee = True
        if role.name == "Head Judge":
            isHeadJudge = True
        if role.name == "Judge":
            isJudge = True
        if role.name == "Team Captain":
            isCaptain = True

    #random sticks     
    rng = random.randint(1,500)
    #stick = discord.utils.get(message.guild.emojis, name='corgistick') 
    stick = client.get_emoji(735827082151723029)
    #lurk = client.get_emoji(736190606254145548)
    #print("Random Number was: " + str(rng))
    if rng % 50 == 0:        
        if stick:
            await message.add_reaction(stick)
    
    if rng == 100:        
        image = directory + "/images/corgilurk.gif"
        await message.channel.send(file=discord.File(image))

    if "corgistick" in message.content:
        response = "No take! *Only* throw."
        await message.channel.send(response.format(message))

    if "wednesday" in message.content.lower():
        day_name= ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday","Sunday"]
        day = datetime.utcnow().weekday()
        if day_name[day] == "Wednesday":
            image = directory + "/images/wednesday.jpg"
            await message.channel.send(file=discord.File(image))

    if message.clean_content.lower() == "time for bed @corgi":
        response = "*Stretches and gets into bed.*"
        await message.channel.send(response.format(message))
        sys.exit()
        return

    if message.content.lower() == "$help":
        response = "Please visit the following link for help on my available commands: <http://fishcord.larnu.uk>"
        await message.channel.send(response.format(message))
        return

    if message.content.lower() == "how i throw":
        rules = throwrules()
        for rule in rules:
            await message.channel.send(rule.format(message))
        return

    if message.content.lower() == "how i slam":
        rules = slamrules()
        for rule in rules:
            await message.channel.send(rule.format(message))
        return

    for mentions in message.mentions:
        if mentions.id == message.guild.me.id:
            await message.channel.send("Woof?")
            break

    if message.content.lower() == ("$github"):
        response = "You can find my master's github here: https://github.com/LarnuUK"
        await message.channel.send(response.format(message))
        return

    if message.content.lower() == "$timezones":
        response = ""
        embed = discord.Embed(title="Available Timezones", description="Timezones available for the conversion commands (such as `$CEST` and `$NZDT`)", color=colourings["dark gold"])
        for tz in timezones:
            tzdata = timezones[tz]
            tzname = tzdata["Name"]
            tzoffset = tzdata["Offset"]
            #tzhours = tzdata["Hours"]
            #tzminutes = tzdata["Minutes"]
            if tzoffset < 0:
                offset = str(tzoffset)
            else:
                offset = "+" + str(tzoffset)
            response = response + "\n**" + tz + "**: " + tzname + " (UTC " + offset + ")"
            #embed.add_field(name=tz, value=tzname + " (UTC" + offset + ")", inline=False)
        # await message.channel.send(response.format(message))
        embed.add_field(name="Timezones", value=response, inline=False)
        await message.channel.send(embed=embed)
        return

    if message.content.lower().startswith("$") and " " in message.content:
        if validatetz(message.content.upper()[1:message.content.index(" ")]):
            spaceindex = message.content.index(" ")
            sourcetz = message.content.upper()[1:spaceindex]
            time = message.content[spaceindex+1:spaceindex+6]
            hours = message.content[spaceindex+1:spaceindex+3]
            minutes = message.content[spaceindex+4:spaceindex+6]
            desttz = message.content.upper()[spaceindex+7:]
            if re.match("[0-9][0-9]:[0-5][0-9]",time):
                try:
                    tzdestination = timezones[desttz]
                    tzsource = timezones[sourcetz]
                except:
                    response = "Invalid or unrecognised timezone. Use $Timezones for a full list of timezones I can convert from CEST."
                    await message.channel.send(response.format(message))
                    return
                tzdesthours = tzdestination["Hours"]
                tzdestminutes = tzdestination["Minutes"]
                tzdestname = tzdestination["Name"]
                tzsourcehours = tzsource["Hours"]
                tzsourceminutes = tzsource["Minutes"]
                tzsourcename = tzsource["Name"]
                newhours = int(hours) - tzsourcehours + tzdesthours
                newminutes = int(minutes) - tzsourceminutes + tzdestminutes
                day = ""
                if newminutes > 59:
                    newminutes = newminutes - 30
                    newhours = newhours + 1
                elif newminutes < 0:
                    newminutes = newminutes + 30
                    newhours = newhours - 1
                if newhours > 23:
                    newhours = newhours - 24
                    day = " (+1 day)"
                elif newhours < 0:
                    newhours = newhours + 24
                    day = " (-1 day)"
                response = time + " " + sourcetz + " (" + tzsourcename + ") is " +  ("00" + str(newhours))[-2:] + ":" + ("00" + str(newminutes))[-2:] + " " + desttz +" (" + tzdestname + ")" + day + "."
                await message.channel.send(response.format(message))
            else:
                response = "Invalid Time format. Must be in format `hh:mm`."
                await message.channel.send(response.format(message))
            return

    if message.content.lower() == ("$roll"):
        i = random.randint(1,6)
        response = "You rolled a " + str(i) + " {0.author.mention}."
        await message.channel.send(response.format(message))
        return

    if message.content.lower().startswith("$roll "):
        dice = message.content[6:]
        if re.match("[0-9]+d[0-9]+",dice):
            die = int(dice[0:dice.find("d")])
            sides = int(dice[dice.find("d")+1:])
            if die > 20:
                response = "Cannot roll more than 20 die at a time."
                await message.channel.send(response.format(message))
            elif sides > 100 or sides < 1:
                response = "Sides cannot be greater than 100."
                await message.channel.send(response.format(message))
            else:
                rolls = []
                r = 0
                total = 0
                rollstr = ""
                while r < die:
                    i = random.randint(1,sides)
                    rolls.append(i)
                    total = total + i
                    rollstr = rollstr + ", " + str(i)
                    r = r+1
                response = "You rolled a total of " + str(total) + " {0.author.mention}: (" + rollstr[2:] + ")"
                await message.channel.send(response.format(message))
            return
        else:
            response = "Unrecognised die format. Use `{{n}}d{{s}}`. For example 2d6 or 1d3."
            await message.channel.send(response.format(message))
            return

    if message.content.lower() == ("$flip"):
        i = random.randint(0,1)
        if i == 0:
            response = "It's Heads!"
        else:
            response = "It's Tails!"
        await message.channel.send(response.format(message))
        return

    #Find Bot-logs channel. There is probably a better way than this though.
    for channel in message.guild.channels:
        if channel.name == "corgi-logs":
            logchannel = channel
            break

    #Timer commands
    if message.content.lower() == "$timer":
        await message.channel.send("The $timer command must be followed by a time period, and optionally a reason. For example: `$timer 03:00` will set a timer for 3 hours. If you wish, you can include a reason afterwards. For example: `$timer 01:30 Ryan and Thom's game` will set a timer for 1 hour 30 minutes with the reason *\"Ryan and Thom's game\"*.")
        return

    if message.content.lower().startswith("$timer "):
        timer = message.content[7:12]
        hours = message.content[7:9]
        minutes = message.content[10:12]
        seconds = "00"
        reason = message.clean_content[13:]
        if re.match("[0-9][0-9]:[0-5][0-9]",timer):
            response = "Setting timer for " + str(int(hours)) + " hour(s) and " + str(int(minutes)) + " minute(s). Let the count down begin!"
            await message.channel.send(response.format(message))
            
            duration = int(seconds) + (int(minutes) * 60) + (int(hours) * 60 *60)
            now = datetime.utcnow()
            embed = discord.Embed(title="Timer", description=reason, color=0x4444dd)
            embed.add_field(name="Duration", value="`" + '%02d' % int(hours) + ":" + '%02d' % int(minutes) + ":" + '%02d' % int(seconds) + "` ", inline=True) 
            embed.add_field(name="Remaining", value="`" + '%02d' % int(hours) + ":" + '%02d' % int(minutes) + ":" + '%02d' % int(seconds) + "` ", inline=True) 
            embed.set_footer(text="Updated at: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
            timermsg = await message.channel.send(embed=embed)
            
            #Start counting down
            start = datetime.now()
            end = start + timedelta(seconds=duration)
            i = 0
            import time
            while datetime.now() < end:
                time.sleep(0.5)
                i = i+1
                remaining = int((end - datetime.now()).total_seconds())
                hours = str(int(remaining / 3600))
                minutes = str(int((remaining % 3600)/60))
                seconds = str(remaining % 60)
                if (remaining >= 600 and i == 30) or (remaining >= 30 and remaining < 600 and i >= 10) or (remaining < 30 and i >= 5) or remaining <= 5:
                    now = datetime.utcnow()
                    embed.set_field_at(1,name="Remaining", value="`" + '%02d' % int(hours) + ":" + '%02d' % int(minutes) + ":" + '%02d' % int(seconds) + "` ", inline=True) 
                    embed.set_footer(text="Updated at: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                    await timermsg.edit(embed=embed)
                    i = 0
            
            #timer complete!
            embed.set_field_at(1,name="Remaining", value="`00:00:00` ", inline=True) 
            await timermsg.edit(embed=embed)
            response = "Your timer has finished {0.author.mention}!".format(message)
            await message.channel.send(response)
        else:
            await message.channel.send("That isn't a valid time!")
        return

    if message.content.lower() == "$heret":
        response = "The $heret command must be followed by a time period and a reason. For example: `$heret 03:00 dice down` will set a timer for 3 hours the reason *\"dice down\"*."
        await message.channel.send(response.format(message))
        return

    if message.content.lower().startswith("$heret "):
        timer = message.content[7:12]
        hours = message.content[7:9]
        minutes = message.content[10:12]
        seconds = "00"
        reason = message.content[13:]
        if reason == "":
            await message.channel.send("Here timers must have a reason.")
            return
        if isowner(message.guild,message.author) or isadmin(message.guild,message.author) or isheadjudge(message.guild,message.author): 
            
            if re.match("[0-9][0-9]:[0-5][0-9]",timer):
                response = "Setting timer for " + str(int(hours)) + " hour(s) and " + str(int(minutes)) + " minute(s). Let the count down begin!"
                await message.channel.send(response.format(message))
                
                duration = int(seconds) + (int(minutes) * 60) + (int(hours) * 60 *60)
                now = datetime.utcnow()
                embed = discord.Embed(title="Here Timer", description=reason, color=0x4444dd)
                embed.add_field(name="Duration", value="`" + '%02d' % int(hours) + ":" + '%02d' % int(minutes) + ":" + '%02d' % int(seconds) + "` ", inline=True) 
                embed.add_field(name="Remaining", value="`" + '%02d' % int(hours) + ":" + '%02d' % int(minutes) + ":" + '%02d' % int(seconds) + "` ", inline=True) 
                embed.set_footer(text="Updated at: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                timermsg = await message.channel.send(embed=embed)
                
                #Start counting down
                start = datetime.now()
                end = start + timedelta(seconds=duration)
                i = 0
                import time
                while datetime.now() < end:
                    i = i+1
                    time.sleep(0.5)
                    remaining = int((end - datetime.now()).total_seconds())
                    hours = str(int(remaining / 3600))
                    minutes = str(int((remaining % 3600)/60))
                    seconds = str(remaining % 60)
                    if (remaining >= 600 and i == 30) or (remaining >= 30 and remaining < 600 and i >= 10) or (remaining < 30 and i >= 5) or remaining <= 5:
                        now = datetime.utcnow()
                        embed.set_field_at(1,name="Remaining", value="`" + '%02d' % int(hours) + ":" + '%02d' % int(minutes) + ":" + '%02d' % int(seconds) + "` ", inline=True) 
                        embed.set_footer(text="Updated at: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                        await timermsg.edit(embed=embed)
                        i = 0
                #timer complete!
                embed.set_field_at(1,name="Remaining", value="`00:00:00`", inline=True) 
                await timermsg.edit(embed=embed)
                response = "".join(["@here , the timer has finished! ", reason]).format(message)
                await message.channel.send(response)
            else:
                await message.channel.send("That isn't a valid time!")
        else:
            await message.channel.send("You must be a Judge to use Here Timers.")
        return

    if message.content.lower().startswith("$germanpairing"):
        if str(message.channel).lower().startswith("table"):
            if len(message.mentions) == 1:
                await germanpairing(message)
            else:
                response = "You must mention your opponent to begin a pairing process."
                await message.channel.send(response.format(message))
        else:
            response = "You can only use this command in a table channel."
            await message.channel.send(response.format(message))
        return

    #Want these commands in the right channel
    if str(message.channel).lower().startswith("bot"):

        if message.content.lower().startswith("$addroleaccess"):
            await addaccess(message,serverRoles)
            return
        
        if message.content.lower().startswith("$removeroleaccess"):
            await removeaccess(message)
            return
        
        if message.content.lower().startswith("$checkroleaccess"):
            await checkaccess(message)
            return

        #The old commands start below here:
        if not(message.guild.id == 721685559277256806):
            return
        
        if message.content.lower() == "$rolestats":
            if isCommittee == False and isHeadJudge == False:
                await message.channel.send("Only Committee members can use that command.")
            else:
                embed = discord.Embed(title="Role Statistics", color=discord.Colour.green())
                guild = message.guild
                guildroles = guild.roles
                members = guild.members
                for guildrole in guildroles:
                    print("Getting count for " + guildrole.name)
                    membercount = 0
                    for member in members:
                        for memberrole in member.roles:
                            if memberrole.name == guildrole.name:
                                membercount += 1
                    embed.add_field(name=guildrole.name, value=membercount, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Reported: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
                response = "Role stats have been sent to the Log Channel"
                await message.channel.send(response.format(message))
                    
            return

        if message.content.lower() == "$colours":
            response = "You can choose from any of the following colours: *" + ", ".join(colours) + "*. Alternatively you can use random for a random colour, or provide your own 6 digit hex code."
            await message.channel.send(response.format(message))
            return

        #Give someone the Team Captain Rank
        if message.content.lower().startswith("$addcaptain"):
            if isCommittee == False and isHeadJudge == False:
                await message.channel.send("Only Committee members can use that command.")
            elif len(message.mentions) == 0:
                await message.channel.send("Needs a user to give Team Captain role.")
            elif len(message.mentions[0].roles) > 1:
                await message.channel.send("User already has a server role and cannot be made a captain.")
            else:
                role = discord.utils.get(message.guild.roles, name="Team Captain")
                await message.mentions[0].add_roles(role)
                response = "{0.mentions[0].display_name} has been given the Team Captain Role."
                await message.channel.send(response.format(message))
                dm = """Hi, you've been given the Team Captain role in the Warmachine and Hordes Virtual Team Championship!

To get started, you'll want to create your team using the `$teamname` command in the bot-commands channel. Once you've done that, you'll have access to all the table channels, and your team will have it's own channel category created. If you''re not completely decided on a name yet, don't worry, you can change it again later using the same command.

Once your team has been created, you can start adding people to the team using the `$addplayer` command. You can also choose the colour of your team's role using $teamcolour. To get your team members in the server, please use this link: https://discord.gg/Xq7fwjF

If you get stuck, just visit the guide in the #bot-help channel: <https://discordapp.com/channels/721685559277256806/721693621413478420/722049487874424892>

Thanks for joining the tournament, and good luck!"""
                newcaptain = client.get_user(message.mentions[0].id)
                await newcaptain.send(dm.format(message))
                #Log details
                embed = discord.Embed(title="Add Team Captain", color=0xa551be) #description=message.mentions[0].display_name
                embed.add_field(name="Added By", value=message.author.display_name, inline=False)
                embed.add_field(name="Added ID", value=message.author.id, inline=False)
                embed.add_field(name="Captain Added", value=message.mentions[0].display_name, inline=False)
                embed.add_field(name="Captain ID", value=message.mentions[0].id, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
            return
        
        #Remove Captain Role from a User
        if message.content.lower().startswith("$removecaptain"):
            if isCommittee == False and isHeadJudge == False:
                await message.channel.send("Only Committee members can use that command.")
            elif len(message.mentions) == 0:
                await message.channel.send("Needs a user to give Team Captain role.")
            elif len(message.mentions[0].roles) > 2:
                if message.mentions[0].roles[1].name == "Team Captain":
                    teamrole = message.mentions[0].roles[2]
                else:
                    teamrole = message.mentions[0].roles[1]
                response = "User has already created a Team. Do you want to delete the team, or make a different member of the Team the captain? To delete the team, respond with \"`DELETE " + teamrole.name.upper() + "`\" (*this action cannot be undone*). To change the captain to a different member, please ping the new captain."
                await message.channel.send(response.format(message))
                def sameuserchannel(m):
                    return m.channel == message.channel and m.author == message.author
                try:
                    reply = await client.wait_for('message',check=sameuserchannel,timeout=60)
                except:
                    response = "No response received. Removal cancelled"
                    await message.channel.send(response.format(message))
                    return
                if reply.content == "DELETE " + teamrole.name.upper():
                    response = "Deleting Team " + teamrole.name + "."
                    await message.channel.send(response.format(message))
                    guildcategories = message.guild.categories
                    for category in guildcategories:
                        if category.name.lower() == teamrole.name.lower():
                            channels = category.channels
                            for channel in channels:
                                await channel.delete()
                            await category.delete()
                            break
                    response = "The team " + teamrole.name + " has been deleted."
                    await message.channel.send(response.format(message))
                    colour = teamrole.color
                    embed = discord.Embed(title="Team Deleted", color=colour) #description=message.mentions[0].display_name
                    embed.add_field(name="Removed By", value=message.author.display_name, inline=False)
                    embed.add_field(name="Removed ID", value=message.author.id, inline=False)
                    embed.add_field(name="Team Name", value=teamrole.name, inline=False)
                    now = datetime.utcnow()
                    embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                    await logchannel.send(embed=embed)
                    await teamrole.delete()
                    role = discord.utils.get(message.guild.roles, name="Team Captain")
                    await message.mentions[0].remove_roles(role)
                    response = "{0.mentions[0].display_name} has been removed from the Team Captain Role."
                    await message.channel.send(response.format(message))
                    embed = discord.Embed(title="Remove Team Captain", color=0xa551be) #description=message.mentions[0].display_name
                    embed.add_field(name="Removed By", value=message.author.display_name, inline=False)
                    embed.add_field(name="Removed ID", value=message.author.id, inline=False)
                    embed.add_field(name="Captain Removed", value=message.mentions[0].display_name, inline=False)
                    embed.add_field(name="Captain ID", value=message.mentions[0].id, inline=False)
                    now = datetime.utcnow()
                    embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                    await logchannel.send(embed=embed)
                elif len(reply.mentions) == 1:
                    inteam = False;
                    for replyrole in reply.mentions[0].roles:
                        if replyrole.name == teamrole.name:
                            inteam = True;
                            break
                    if inteam == True:
                        response = "{0.mentions[0].display_name} has been removed from the Team Captain Role."
                        await message.channel.send(response.format(message))
                        role = discord.utils.get(message.guild.roles, name="Team Captain")
                        await message.mentions[0].remove_roles(role)
                        response = "{0.mentions[0].display_name} has been removed from the Team Captain Role."
                        embed = discord.Embed(title="Remove Team Captain", color=0xa551be) #description=message.mentions[0].display_name
                        embed.add_field(name="Removed By", value=message.author.display_name, inline=False)
                        embed.add_field(name="Removed ID", value=message.author.id, inline=False)
                        embed.add_field(name="Captain Removed", value=message.mentions[0].display_name, inline=False)
                        embed.add_field(name="Captain ID", value=message.mentions[0].id, inline=False)
                        now = datetime.utcnow()
                        embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                        await logchannel.send(embed=embed)
                        response = reply.mentions[0].display_name + " has been added to the Team Captain Role."
                        await message.channel.send(response.format(message))
                        await reply.mentions[0].add_roles(role)
                        embed = discord.Embed(title="Add Team Captain", color=0xa551be) #description=message.mentions[0].display_name
                        embed.add_field(name="Added By", value=message.author.display_name, inline=False)
                        embed.add_field(name="Added ID", value=message.author.id, inline=False)
                        embed.add_field(name="Captain Added", value=reply.mentions[0].display_name, inline=False)
                        embed.add_field(name="Captain ID", value=reply.mentions[0].id, inline=False)
                        now = datetime.utcnow()
                        embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                        await logchannel.send(embed=embed)
                    else:
                        response = "User is not in the same team. YOu can only promote a member in the same team. Aborted removing {0.mentions[0].display_name} from the Team Captain Role."
                        await message.channel.send(response.format(message))
                else:
                    response = "Aborted removing {0.mentions[0].display_name} from the Team Captain Role."
                    await message.channel.send(response.format(message))
            else:
                role = discord.utils.get(message.guild.roles, name="Team Captain")
                await message.mentions[0].remove_roles(role)
                response = "{0.mentions[0].display_name} has been removed from the Team Captain Role."
                embed = discord.Embed(title="Remove Team Captain", color=0xa551be) #description=message.mentions[0].display_name
                embed.add_field(name="Removed By", value=message.author.display_name, inline=False)
                embed.add_field(name="Removed ID", value=message.author.id, inline=False)
                embed.add_field(name="Captain Removed", value=message.mentions[0].display_name, inline=False)
                embed.add_field(name="Captain ID", value=message.mentions[0].id, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
            return

        #Give someone the Judge Rank
        if message.content.lower().startswith("$addjudge"):
            if isCommittee == False:
                await message.channel.send("Only Committee members can use that command.")
            elif len(message.mentions) == 0:
                await message.channel.send("Needs a user to give Judge role.")
            else:
                roles = message.mentions[0].roles
                inteam = False
                for role in roles:
                    if role.name.lower() == "judge":
                        await message.channel.send("User is already a Judge...")    
                        return
                    elif role.name.lower() not in ("head judge","vtc committee","@everyone"):
                        inteam = True
                        break
                if inteam == True:
                    await message.channel.send("User is in a team and cannot be made a Judge.")
                else:
                    role = discord.utils.get(message.guild.roles, name="Judge")
                    await message.mentions[0].add_roles(role)
                    response = "{0.mentions[0].display_name} has been given the Judge Role."
                    await message.channel.send(response.format(message))
                    #Log details
                    embed = discord.Embed(title="Add Judge", color=discord.Colour.blue()) #description=message.mentions[0].display_name
                    embed.add_field(name="Added By", value=message.author.display_name, inline=False)
                    embed.add_field(name="Added ID", value=message.author.id, inline=False)
                    embed.add_field(name="Judge Added", value=message.mentions[0].display_name, inline=False)
                    embed.add_field(name="Judge ID", value=message.mentions[0].id, inline=False)
                    now = datetime.utcnow()
                    embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                    await logchannel.send(embed=embed)
            return


        #Give someone the Judge Rank
        if message.content.lower().startswith("$addheadjudge"):
            if isCommittee == False:
                await message.channel.send("Only Committee members can use that command.")
            elif len(message.mentions) == 0:
                await message.channel.send("Needs a user to give Head Judge role.")
            else:
                roles = message.mentions[0].roles
                inteam = False
                for role in roles:
                    if role.name.lower() == "head judge":
                        await message.channel.send("User is already a Head Judge...")    
                        return
                    elif role.name.lower() not in ("judge","vtc committee","@everyone"):
                        inteam = True
                        break
                if inteam == True:
                    await message.channel.send("User is in a team and cannot be made a Judge.")
                else:
                    role = discord.utils.get(message.guild.roles, name="Judge")
                    await message.mentions[0].add_roles(role)
                    role = discord.utils.get(message.guild.roles, name="Head Judge")
                    await message.mentions[0].add_roles(role)
                    response = "{0.mentions[0].display_name} has been given the Head Judge Role."
                    await message.channel.send(response.format(message))
                    #Log details
                    embed = discord.Embed(title="Add Head Judge", color=discord.Colour.dark_blue()) #description=message.mentions[0].display_name
                    embed.add_field(name="Added By", value=message.author.display_name, inline=False)
                    embed.add_field(name="Added ID", value=message.author.id, inline=False)
                    embed.add_field(name="Head Judge Added", value=message.mentions[0].display_name, inline=False)
                    embed.add_field(name="Head Judge ID", value=message.mentions[0].id, inline=False)
                    now = datetime.utcnow()
                    embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                    await logchannel.send(embed=embed)
            return

        if message.content.lower().startswith("$removejudge"):
            if isCommittee == False:
                await message.channel.send("Only Committee members can use that command.")
                return
            elif len(message.mentions) == 0:
                await message.channel.send("Needs a user to remove Streamer role.")
                return
            else:
                if len(message.mentions[0].roles) < 2:
                    await message.channel.send("User does not have the Judge Role to remove.")
                elif len(message.mentions[0].roles) == 2:
                    role = message.mentions[0].roles[1]
                    if role.name == "Judge":
                        await message.mentions[0].remove_roles(role)
                        response = "{0.mentions[0].display_name} has been removed from the Judge Role."
                        await message.channel.send(response.format(message))
                        #Log details
                        embed = discord.Embed(title="Remove Player as Judge", color=discord.Colour.blue()) 
                        embed.add_field(name="Removed By", value=message.author.display_name, inline=False)
                        embed.add_field(name="Removed ID", value=message.author.id, inline=False)
                        embed.add_field(name="Removed Player", value=message.mentions[0].display_name, inline=False)
                        embed.add_field(name="Removed ID", value=message.mentions[0].id, inline=False)
                        now = datetime.utcnow()
                        embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                        await logchannel.send(embed=embed)
                    else:
                        await message.channel.send("User does not have the Judge Role to remove.")
                else:
                    role1 = message.mentions[0].roles[1]
                    role2 = message.mentions[0].roles[2]
                    if role2.name == "Judge" or role2.name == "Head Judge":
                        await message.mentions[0].remove_roles(role2)
                        response = "{0.mentions[0].display_name} has been removed from the " + role2.name + " role."
                        await message.channel.send(response.format(message))
                        if role2.name == "Judge":
                            colour = discord.Colour.blue()
                        else:
                            colour = discord.Colour.dark_blue()
                        #Log details
                        embed = discord.Embed(title="Remove Player as " + role2.name, color=colour) 
                        embed.add_field(name="Removed By", value=message.author.display_name, inline=False)
                        embed.add_field(name="Removed ID", value=message.author.id, inline=False)
                        embed.add_field(name="Removed Player", value=message.mentions[0].display_name, inline=False)
                        embed.add_field(name="Removed ID", value=message.mentions[0].id, inline=False)
                        now = datetime.utcnow()
                        embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                        await logchannel.send(embed=embed)
                    if role1.name == "Judge" or role1.name == "Head Judge":
                        await message.mentions[0].remove_roles(role1)
                        response = "{0.mentions[0].display_name} has been removed from the " + role1.name + " role."
                        await message.channel.send(response.format(message))
                        if role1.name == "Judge":
                            colour = discord.Colour.blue()
                        else:
                            colour = discord.Colour.dark_blue()
                        #Log details
                        embed = discord.Embed(title="Remove Player as " + role1.name, color=colour) 
                        embed.add_field(name="Removed By", value=message.author.display_name, inline=False)
                        embed.add_field(name="Removed ID", value=message.author.id, inline=False)
                        embed.add_field(name="Removed Player", value=message.mentions[0].display_name, inline=False)
                        embed.add_field(name="Removed ID", value=message.mentions[0].id, inline=False)
                        now = datetime.utcnow()
                        embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                        await logchannel.send(embed=embed)
                return

        #Give someone the Judge Rank
        if message.content.lower().startswith("$addstreamer"):
            if isCommittee == False:
                await message.channel.send("Only Committee members can use that command.")
            elif len(message.mentions) == 0:
                await message.channel.send("Needs a user to give Streamer role.")
            elif len(message.mentions[0].roles) > 1:
                await message.channel.send("User already has a server role and cannot be made a Streamer.")
            else:
                role = discord.utils.get(message.guild.roles, name="Streamer")
                await message.mentions[0].add_roles(role)
                response = "{0.mentions[0].display_name} has been given the Streamer Role."
                await message.channel.send(response.format(message))
                #Log details
                embed = discord.Embed(title="Add Streamer", color=0x9147ff) 
                embed.add_field(name="Added By", value=message.author.display_name, inline=False)
                embed.add_field(name="Added ID", value=message.author.id, inline=False)
                embed.add_field(name="Judge Added", value=message.mentions[0].display_name, inline=False)
                embed.add_field(name="Judge ID", value=message.mentions[0].id, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
            return

        if message.content.lower().startswith("$removestreamer"):
            if isCommittee == False:
                await message.channel.send("Only Committee members can use that command.")
            elif len(message.mentions) == 0:
                await message.channel.send("Needs a user to remove Streamer role.")
            else:
                role = message.mentions[0].roles[1]
                if role.name == "Streamer":
                    await message.mentions[0].remove_roles(role)
                    response = "{0.mentions[0].display_name} has been removed from the Streamer Role."
                    await message.channel.send(response.format(message))
                    #Log details
                    embed = discord.Embed(title="Remove Player as Streamer", color=0x9147ff) 
                    embed.add_field(name="Removed By", value=message.author.display_name, inline=False)
                    embed.add_field(name="Removed ID", value=message.author.id, inline=False)
                    embed.add_field(name="Removed Player", value=message.mentions[0].display_name, inline=False)
                    embed.add_field(name="Removed ID", value=message.mentions[0].id, inline=False)
                    now = datetime.utcnow()
                    embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                    await logchannel.send(embed=embed)
                else:
                    await message.channel.send("User does not have the Streamer Role to remove.")
            return

        if message.content.lower().startswith("$teamname"):
            if isCaptain == False:
                await message.channel.send("Only Team Captains can use that command.")
                return
            else:
                teamname = message.content[10:]
                if len(teamname.replace(" ","")) == 0:
                    response = "You need a name for your team, you silly!"
                    await message.channel.send(response)
                    return
                #Check if the team exists
                guild = message.guild
                guildroles = guild.roles
                for guildrole in guildroles:
                    if guildrole.name.lower() == teamname.lower():
                        response = "A role with the name " + guildrole.name +" already exists. Please choose a different name."
                        await message.channel.send(response)
                        return
                    elif guildrole.name == "Team Captain":
                        CaptainRole = guildrole
                        break #Don't forget to get rid of this if we expand in the future.
                    #elif guildrole.name == "VTC Committee":
                    #    CommitteeRole = guildrole
                    #elif guildrole.name == "Judge":
                    #    JudgeRole = guildrole
                    #elif guildrole.name == "Head Judge":
                    #    HeadJudgeRole = guildrole
                guildcategories = guild.categories
                for category in guildcategories:
                    if category.name.lower() == teamname.lower():
                        response = "A category with the name " + category.name +" already exists. Please choose a different name."
                        await message.channel.send(response)
                        return
                #Check Team Captain is already in a Team
                if len(message.author.roles) == 2:
                    newrole = await guild.create_role(name=teamname, hoist=True)
                    colour = int("0x"+str(randomcolour()),16)
                    await newrole.edit(colour=discord.Colour(colour))
                    await newrole.edit(position=2) 
                    await CaptainRole.edit(position=1)
                    response = "Created role " + teamname +"."
                    await message.channel.send(response)
                    role = discord.utils.get(message.guild.roles, name=teamname)
                    await message.author.add_roles(role)
                    await message.channel.send("Setting table permissions... Please hold.")
                    guildchannels = guild.channels
                    for guildchannel in guildchannels:
                        if guildchannel.name.lower().startswith('table'):
                            print(guildchannel.name)
                            if guildchannel.type.name == "text" and "game" in guildchannel.name.lower():
                                print("Setting read and send message permissions")
                                await guildchannel.set_permissions(newrole, read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, use_external_emojis=True,add_reactions=True)
                                #await guildchannel.set_permissions(CommitteeRole, read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, use_external_emojis=True,manage_messages=True,mention_everyone=True,add_reactions=True)
                                #await guildchannel.set_permissions(HeadJudgeRole, read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, use_external_emojis=True,manage_messages=True,mention_everyone=True,add_reactions=True)
                                #await guildchannel.set_permissions(JudgeRole, read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, use_external_emojis=True,mention_everyone=True,add_reactions=True)
                            elif guildchannel.type.name == "voice" and "game" in guildchannel.name.lower():
                                print("Setting connect and speak permissions")
                                await guildchannel.set_permissions(newrole,view_channel=True,connect=True,speak=True)
                                #await guildchannel.set_permissions(CommitteeRole,view_channel=True,connect=True,speak=True,mute_members=True,move_members=True,priority_speaker=True)
                                #await guildchannel.set_permissions(HeadJudgeRole,view_channel=True,connect=True,speak=True,mute_members=True,move_members=True,priority_speaker=True)
                                #await guildchannel.set_permissions(JudgeRole,view_channel=True,connect=True,speak=True,mute_members=True,move_members=True,priority_speaker=True)
                    await message.channel.send("Table Permissions set. Creating team channels.")
                    #Create the Category and Channels
                    newcategory = await guild.create_category(teamname)
                    await newcategory.edit(position=6) 
                    botrole = discord.utils.get(message.guild.roles, name="Bots")
                    talkrights = {guild.default_role: discord.PermissionOverwrite(read_messages=False),botrole: discord.PermissionOverwrite(read_messages=True)}
                    newtalk = await guild.create_text_channel(name="Team Chat",category=newcategory,overwrites=talkrights)
                    await newtalk.set_permissions(newrole, read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, use_external_emojis=True)
                    await newtalk.set_permissions(CaptainRole, manage_messages=True)
                    #await newtalk.set_permissions(CommitteeRole, read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, use_external_emojis=True)
                    #await newtalk.set_permissions(HeadJudgeRole, read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, use_external_emojis=True)
                    chatrights = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
                    newchat = await guild.create_voice_channel(name="Team Talk",category=newcategory,overwrites=chatrights)
                    await newchat.set_permissions(newrole,view_channel=True,connect=True,speak=True)
                    #await newchat.set_permissions(CommitteeRole,view_channel=True,connect=True,speak=True)
                    #await newchat.set_permissions(HeadJudgeRole,view_channel=True,connect=True,speak=True)
                    await message.channel.send("New Team created.")
                    #Log details
                    embed = discord.Embed(title="Create New Team", color=colour) 
                    embed.add_field(name="Created By", value=message.author.display_name, inline=False)
                    embed.add_field(name="Created ID", value=message.author.id, inline=False)
                    embed.add_field(name="Team Name", value=teamname, inline=False)
                    now = datetime.utcnow()
                    embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                    await logchannel.send(embed=embed)

                #They are in one, so edit the Team's name
                else:
                    if message.author.roles[1].name == "Team Captain":
                        teamrole = message.author.roles[2]
                    else:
                        teamrole = message.author.roles[1]
                    categories = guild.categories
                    for category in categories:
                        if category.name == teamrole.name:
                            await category.edit(name=teamname)
                            break
                    embed = discord.Embed(title="Change Team Name", color=teamrole.colour) #description=message.mentions[0].display_name
                    embed.add_field(name="Changed By", value=message.author.display_name, inline=False)
                    embed.add_field(name="Changed ID", value=message.author.id, inline=False)
                    embed.add_field(name="Old Team Name", value=teamrole.name, inline=False)
                    embed.add_field(name="New Team Name", value=teamname, inline=False)
                    now = datetime.utcnow()
                    embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                    await logchannel.send(embed=embed)
                    await teamrole.edit(name=teamname)
                    response = "Team Name has been changed to " + teamname +"."
                    await message.channel.send(response)
                return

        if message.content.lower().startswith("$teamcolour"):
            if isCaptain == False:
                await message.channel.send("Only Team Captains can use that command.")
            else:
                teamcolour = message.content[12:].lower()
                if len(message.author.roles) == 2:
                    await message.channel.send("You need to have created your team before you can set their colour.")
                elif message.content.lower() == "$teamcolour":
                    await message.channel.send("You must supply a colour. Either provide a colour hex, ask for a random colour, or use one of the preprogrammed colours. See `$colours` or <https://htmlcolorcodes.com/color-picker/> for ideas.")
                elif not re.match("[0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]",teamcolour) and colours.count(teamcolour) == 0 and not teamcolour == "random":
                    await message.channel.send("Invalid hex or predefined colour.")
                else:
                    if message.author.roles[1].name == "Team Captain":
                        teamrole = message.author.roles[2]
                    else:
                        teamrole = message.author.roles[1]
                    if colours.count(teamcolour) == 1:
                        colour = colourings[teamcolour]
                        await teamrole.edit(colour=discord.Colour(colour.value))
                        embed = discord.Embed(title="Change Team Colour", color=colour.value) 
                    elif teamcolour == "random":
                        colour = int("0x"+str(randomcolour()),16)
                        await teamrole.edit(colour=discord.Colour(colour))
                        embed = discord.Embed(title="Change Team Colour", color=colour) 
                    else:
                        colour = int("0x"+teamcolour,16)
                        await teamrole.edit(colour=discord.Colour(colour))
                        embed = discord.Embed(title="Change Team Colour", color=colour) 
                    await message.channel.send("Team colour has been changed.")
                    #Log details
                    embed.add_field(name="Changed By", value=message.author.display_name, inline=False)
                    embed.add_field(name="Changed ID", value=message.author.id, inline=False)
                    now = datetime.utcnow()
                    embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                    await logchannel.send(embed=embed)
            return

        if message.content.lower().startswith("$addplayer"):
            if 1 == 1:
                #Hard code, cause lazy.
                await message.channel.send("This command is currently disabled. Please contact the server owner for the time being.")
                return
            if isCaptain == False:
                await message.channel.send("Only Team Captains can use that command.")
            elif len(message.mentions) == 0:
                await message.channel.send("Needs a user to give Team role.")
            elif len(message.mentions[0].roles) > 1:
                await message.channel.send("User already has a server role and cannot be added to a team.")
            else:
                if message.author.roles[1].name == "Team Captain":
                    teamrole = message.author.roles[2]
                else:
                    teamrole = message.author.roles[1]
                await message.mentions[0].add_roles(teamrole)
                response = "{0.mentions[0].display_name} has been added to the team " + teamrole.name + "."
                await message.channel.send(response.format(message))
                #Log details
                embed = discord.Embed(title="Add Player to Team", color=teamrole.color) 
                embed.add_field(name="Team Name", value=teamrole.name, inline=False)
                embed.add_field(name="Added By", value=message.author.display_name, inline=False)
                embed.add_field(name="Added ID", value=message.author.id, inline=False)
                embed.add_field(name="New Player", value=message.mentions[0].display_name, inline=False)
                embed.add_field(name="NewID", value=message.mentions[0].id, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
            return

        if message.content.lower().startswith("$removeplayer"):
            if isCaptain == False:
                await message.channel.send("Only Team Captains can use that command.")
            elif len(message.mentions) == 0:
                await message.channel.send("Needs a user to remove Team role.")
            else:
                if message.author.roles[1].name == "Team Captain":
                    teamrole = message.author.roles[2]
                else:
                    teamrole = message.author.roles[1]
                await message.mentions[0].remove_roles(teamrole)
                response = "{0.mentions[0].display_name} has been removed from the team " + teamrole.name + "."
                await message.channel.send(response.format(message))
                #Log details
                embed = discord.Embed(title="Remove Player from Team", color=teamrole.color) 
                embed.add_field(name="Removed By", value=message.author.display_name, inline=False)
                embed.add_field(name="Removed ID", value=message.author.id, inline=False)
                embed.add_field(name="Removed Player", value=message.mentions[0].display_name, inline=False)
                embed.add_field(name="Removed ID", value=message.mentions[0].id, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
            return

        if message.content.lower() == "$openserver":
            if isThom == False:
                await message.channel.send("Only Thom can use that command.")
            else:
                #get everyone role
                guild = message.guild
                for role in guild.roles:
                    if role.name == "@everyone":
                        everyone = role
                        break
                await message.channel.send("Setting table permissions... Please hold.")
                guildchannels = guild.channels
                for guildchannel in guildchannels:
                        print(guildchannel.name)
                        if guildchannel.type.name == "text" and "game" in guildchannel.name.lower():
                            print("Setting read and send message permissions")
                            await guildchannel.set_permissions(everyone, read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, use_external_emojis=True,add_reactions=True)
                        elif guildchannel.type.name == "voice" and "game" in guildchannel.name.lower():
                            print("Setting connect and speak permissions")
                            await guildchannel.set_permissions(everyone,view_channel=True,connect=True,speak=True)
                await message.channel.send("Server is now open to everyone.")
                embed = discord.Embed(title="Open Server to Public", color=0x22cc22) 
                embed.add_field(name="Opened By", value=message.author.display_name, inline=False)
                embed.add_field(name="Opened ID", value=message.author.id, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
            return

        if message.content.lower() == "$closeserver":
            if isThom == False:
                await message.channel.send("Only Thom can use that command.")
            else:
                #get everyone role
                guild = message.guild
                for role in guild.roles:
                    if role.name == "@everyone":
                        everyone = role
                        break
                await message.channel.send("Setting table permissions... Please hold.")
                guildchannels = guild.channels
                for guildchannel in guildchannels:
                    if guildchannel.name.lower().startswith('table') and not guildchannel.name.lower().endswith('chat') and not guildchannel.name.lower().endswith('talk'):
                        print(guildchannel.name)
                        if guildchannel.type.name == "text" and "game" in guildchannel.name.lower():
                            print("Setting read and send message permissions")
                            await guildchannel.set_permissions(everyone, read_messages=False, send_messages=False, embed_links=False, attach_files=False, read_message_history=False, use_external_emojis=False,add_reactions=False)
                        elif guildchannel.type.name == "voice" and "game" in guildchannel.name.lower():
                            print("Setting connect and speak permissions")
                            await guildchannel.set_permissions(everyone,view_channel=False)
                await message.channel.send("Server is now closed to everyone.")
                embed = discord.Embed(title="Close Server to Public", color=0xcc2222) 
                embed.add_field(name="Opened By", value=message.author.display_name, inline=False)
                embed.add_field(name="Opened ID", value=message.author.id, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
            return

        if message.content.lower() == "$limitvcs":
            if isThom == False:
                await message.channel.send("Only Thom can use that command.")
            else:
                await message.channel.send("Limiting Game VCs to 4 users.")
                guild = message.guild
                guildchannels = guild.channels
                for guildchannel in guildchannels:
                    if guildchannel.name.lower().startswith('table'):
                        print(guildchannel.name)
                        if guildchannel.type.name == "voice" and "game" in guildchannel.name.lower():
                            print("Changing max connected users.")
                            await guildchannel.edit(user_limit=4)
                await message.channel.send("Game VCs are now limited to 4 users.")
                embed = discord.Embed(title="Limit Game VC Connections", color=colourings["orange"]) 
                embed.add_field(name="Limited By", value=message.author.display_name, inline=False)
                embed.add_field(name="Limiting ID", value=message.author.id, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
            return

        if message.content.lower() == "$unlimitvcs":
            if isThom == False:
                await message.channel.send("Only Thom can use that command.")
            else:
                await message.channel.send("Removing Limit on Game VCs.")
                guild = message.guild
                guildchannels = guild.channels
                for guildchannel in guildchannels:
                    if guildchannel.name.lower().startswith('table'):
                        print(guildchannel.name)
                        if guildchannel.type.name == "voice" and "game" in guildchannel.name.lower():
                            print("Changing max connected users.")
                            await guildchannel.edit(user_limit=0)
                await message.channel.send("Game VCs can now have unlimited users.")
                embed = discord.Embed(title="Unlimit Game VC Connections", color=colourings["gold"]) 
                embed.add_field(name="Unlimited By", value=message.author.display_name, inline=False)
                embed.add_field(name="Unlimiting ID", value=message.author.id, inline=False)
                now = datetime.utcnow()
                embed.set_footer(text="Logged: " + now.strftime("%Y-%m-%d %H:%M:%S") + " UTC")
                await logchannel.send(embed=embed)
            return

@client.event
async def on_guild_role_delete(role):
    await removeaccesslevel(role.guild,role)

client.run(key)