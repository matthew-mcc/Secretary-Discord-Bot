from os import name
import discord
import datetime as dt
import time
from discord import message
from discord.enums import Status
from discord.ext import commands
import asyncio
import db
import re

database = db.DataBase()

disc_client = discord.Client()
client = commands.Bot(command_prefix = '#')
client_id = 810231896524193833
client.remove_command("help")
token = input("Enter Token: ")
status = discord.Game("#commands for help")

def setupDB():
    database.createTables()
    database.saveToDB()

@client.event
async def on_ready():
    msg = client.get_channel(client_id)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(status=discord.Status.idle, activity=status)
    setupDB()

@client.event
async def on_reaction_add(reaction,user):
    # print(user)
    # print(type(user))
    channel = reaction.message.channel
    if user.name == "J.A.R.V.I.S.":
        return
    print(user.name)
    if reaction.emoji != '🥰':
        return
    ID = "<@!" + str(user.id) + ">"
    if(database.isNotConfirmed(ID, reaction.message.embeds[0].fields[1].value)):
        await channel.send('{} has confirmed attendance!'.format(user.name))#,reaction.emoji, reaction.message.content))
        embed = discord.Embed(title="Meeting Confirmation", color=0x00FF00)
        embed.add_field(name=reaction.message.embeds[0].fields[0].name, value=reaction.message.embeds[0].fields[0].value)
        embed.add_field(name=reaction.message.embeds[0].fields[1].name, value=reaction.message.embeds[0].fields[1].value)
        embed.add_field(name=reaction.message.embeds[0].fields[2].name, value=reaction.message.embeds[0].fields[2].value)
        await user.send("",embed=embed)
    print(user)
    database.changeStatus(ID, reaction.message.embeds[0].fields[1].value, "yes")

@client.event
async def on_reaction_remove(reaction,user):
    channel = reaction.message.channel
    await channel.send('{} has removed {} to the message: {}'.format(user.name,reaction.emoji, reaction.message.content))

async def reminder(ctx, l):
    set_time = dt.datetime.strptime(l[0],"%Y-%m-%d %H:%M")
    initial_time = dt.datetime.now()
    wait = (set_time - initial_time).total_seconds()
    wait -= 600 
    await asyncio.sleep(wait)
    embed = discord.Embed(title="NOTICE: You Have a Meeting Scheduled in 10 Minutes.")
    # await ctx.message.channel.send(embed=embed)
    result = re.sub('[^0-9]','',l[2])
    user = await client.fetch_user(result)
    await user.send("", embed=embed)

def split(names):
    all = ''
    for i in names:
        all = all + i
    return all

@client.command()
async def setup(ctx, *args):
    args = list(args)
    # print(args)
    copy = args[:]
    if len(args) <= 1:
        embed = discord.Embed(title="Meeting Instructions", color=0xFF22FF)
        embed.add_field(name="First Argument: Date Time", value="Please enter date-time value (year-month-day hour:minute")
        embed.add_field(name="Second Argument: Location", value="Please enter location as second argument as one word or containted within " "")
        embed.add_field(name="Additional Arguments: Names", value="You can enter as many names as you want as command line arguments after the first two.")
        embed.add_field(name="When Ready", value="Create a meeting by using #setup time location names....")
        await ctx.message.channel.send(embed=embed)
    elif len(args) >= 3:
        database.createMeeting(args[1], args[0])
        for p in args[2:]:
            database.createPerson(p)
            database.createAttendance(p, args[1])
        database.saveToDB()
    embed = discord.Embed(title="Meeting Information", color=0xFF00FF)
    embed.add_field(name="Date-Time", value=args[0], inline=True)
    embed.add_field(name="Location", value=args[1], inline=True)
    args.pop(0)
    args.pop(0)
    embed.add_field(name='Names',value= split(args) ,inline=True)
    embed.set_footer(text="Please react " + '🥰' + "if you are able to attend!")
    msg = await ctx.message.channel.send(embed = embed)
    await msg.add_reaction('🥰')
    await reminder(ctx, copy)

@client.command()
async def allSchedule(ctx):
    embed = discord.Embed(title="Displaying current meetings", color=0xFF00FF)
    meetingsList = database.displayAllMeetings().split("\n")
    topic = ""
    date = ""
    for i in meetingsList:
        tempList = i.split(" ")
        topic = topic + tempList[0] + "\n"
        date = date + tempList[1] + tempList[2] + "\n"
    embed.add_field(name="Meeting Topic", value=topic, inline=True)
    embed.add_field(name="Date-Time", value=date, inline=True)
    await ctx.message.channel.send(embed=embed)

@client.command()
async def mySchedule(ctx):
    embed = discord.Embed(title="Displaying Personal Meetings", color=0xFF00FF)
    ID = "<@!" + str(ctx.message.author.id) + ">"
    # print(ID)
    meetingsList = database.personalMeetings(ID).split("\n")
    topic = ""
    date = ""
    for i in meetingsList:
        tempList = i.split(" ")
        # print(tempList)
        topic = topic + tempList[0] + "\n"
        date = date + tempList[1] + tempList[2] + "\n"
    embed.add_field(name="Meeting Topic", value=topic, inline=True)
    embed.add_field(name="Date-Time", value=date, inline=True)
    await ctx.message.channel.send(embed=embed)


# My Help Button
@client.command("commands")
async def commands(context):
    msg = client.get_channel(client_id)
    helplist = discord.Embed(title="Commands", description="Prefix for all commands is #", color=0xFF00FF)
    helplist.add_field(name="commands", value="Shows commands.", inline=True)
    helplist.add_field(name="setup", value = "Commands for setting up group meetings", inline=False)
    helplist.add_field(name="allSchedule", value="Command to view all upcoming meetings in order (soonest to furthest)", inline=False)
    helplist.add_field(name="mySchedule", value="Command to view personal upcoming confirmed meetings (soonest to furthest).", inline=False)
    await context.message.channel.send(embed = helplist)
#Run the client on the server
client.run(token)
