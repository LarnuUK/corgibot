import discord, discord.utils, random, os, re, json, sys, time, secrets, pyodbc
from datetime import datetime, timedelta
from dotenv import load_dotenv

from access import isowner, isadmin, isheadjudge, isjudge, iscaptain, getcaptain
from events import getevent

load_dotenv()
SQLServer = os.getenv('SQL_SERVER')
SQLDatabase = os.getenv('SQL_DATABASE')
SQLLogin = os.getenv('SQL_LOGIN')
SQLPassword = os.getenv('SQL_PASSWORD')

SQLConnString = 'Driver={ODBC Driver 17 for SQL Server};Server=' + SQLServer + ';Database=' + SQLDatabase + ';UID='+ SQLLogin +';PWD=' + SQLPassword

#sqlConn = pyodbc.connect(SQLConnString,timeout=20)

def validint(string):
    try:
        intval = int(string)
        return True
    except:
        return False

async def redeempurchase(client,message):
    def isUser(m):
        return m.author.id == message.author.id and m.channel.type == discord.ChannelType.private

    dm = """Thank you for purchasing from Fishcord! In order to redeem your Fishcon Ticket, or Fishmachine benefit, I'll need to check a few details first. Please reply with your order number, which you can find in your confirmation email in both the email subject and the top right of the email content.

*Please note that messages regarding purchase redemption are logged, and will be retained until shortly after the conclusion of Fishcon 2021. Please contact a member of the Fishcon Committee should you have any concerns.*"""
    await message.author.send(dm.format(message))
    orderno = await client.wait_for('message',check=isUser,timeout=300)
    while not validint(orderno.content):
        dm = "I'm sorry, that isn't a valid order number. Please enter a valid order number. For example 7890."
        await message.author.send(dm.format(message))
        orderno = await client.wait_for('message',check=isUser,timeout=150)
    dm = "Thanks! Can you also please confirm the email address that you used to make your purchase."
    await message.author.send(dm.format(message))
    email = await client.wait_for('message',check=isUser,timeout=150)
    dm = "Thanks. I am now validating your details."
    await message.author.send(dm.format(message))
    with pyodbc.connect(SQLConnString,timeout=20) as sqlConn:
        with sqlConn.cursor() as cursor:
            try:
                cursor.execute('EXEC corgi.ValidatePurchase ?, ?;',orderno.content,email.content)
            except pyodbc.Error as ex:
                dm = "Error: " + ex.args[0] + " - " + ex.args[1]
                await message.author.send(dm.format(message))
                dm = "Sorry I was unable to redeem you ticket due to an error. Please contact a member of the Fishcon Committee (you can ping them in Fiscord with `@Fishcord Committee`) whom will be able to help you."
                await message.author.send(dm.format(message))
                #cursor.close()
                return
            sku = None
            purchaseID = None
            for row in cursor:
                sku = row[0]
                purchaseID = row[1]
            #cursor.close()
        if sku is None:
            dm = "Unfortunately I was unable to find your Fishcon ticket purchase with the information supplied. If you would like to try again, please use the $redeem command again. If you continue to fail validation, please contact a member of the Fishcon Committee, and they will be happy to help."
            await message.author.send(dm.format(message))
        elif sku.startswith("FISC"):
            fishconroleid = 787360415524716564
            fishconrole = discord.utils.get(message.guild.roles, id=fishconroleid)
            await message.author.add_roles(fishconrole)
            dm = "Purchase located! I have now added your Fishcon 2021 role to your User in the Fishcord Server. Enjoy the event, and thank you for purchasing a ticket. :corgiball: "
            await message.author.send(dm.format(message))
            with sqlConn.cursor() as cursor:
                cursor.execute('EXEC corgi.RedeemPurchase ?;',purchaseID)
                cursor.commit()
                #cursor.close()
    return