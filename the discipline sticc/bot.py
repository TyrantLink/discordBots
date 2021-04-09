import os
import logging
import discord
from random import randint
from pickle import load,dump
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

saveFile = 'save.dat'
client = commands.Bot(command_prefix='sticc!')
client.remove_command('help')
tsRole = discord.Object('769298891068669974')
serverId = 559830737889787924
os.chdir(r"S:\ProgrammingProjects\&DiscordBots\the discipline sticc")
logging.basicConfig(format='[%(asctime)s.%(msecs)03d] %(message)s',filename='output.log',level=logging.WARNING,datefmt='%d/%m/%Y %H:%M:%S')
load_dotenv()
token=os.getenv('token')
logModes = {'r':'responded ','s':'status changed to ','n':''}
bannedUsers = ['343972120067309568']
admins = ['344912616629469184','434133025450754058','250797109022818305']
daysConv = {'monday':0,'tuesday':1,'wednesday':2,'thursday':3,'friday':4,'saturday':5,'sunday':6}
daysConvR= {0:'monday',1:'tuesday',2:'wednesday',3:'thursday',4:'friday',5:'saturday',6:'sunday'}

with open(saveFile,'rb') as save:
    activeMemberNames = load(save)
    activeMemberIDs = load(save)
    currentStik = load(save)
    updateDays = load(save)
    sticcs = load(save)
    idNameCache = load(save)
def saveAll():
    with open(saveFile,'wb') as save:
        dump(activeMemberNames,save)
        dump(activeMemberIDs,save)
        dump(currentStik,save)
        dump(updateDays,save)
        dump(sticcs,save)
        dump(idNameCache,save)
def logEvent(ctx,text,custom=False,mode='n'):
    try: m=logModes[mode]
    except: m='unknown log mode'
    log=f"{m}{text} in {ctx.guild} - {ctx.channel}" if custom == False else f'{text}'
    logging.warning(log)
    print(log)
async def activeMembers(ctx):
    activeMemberNames.append(str(ctx.author))
    activeMemberIDs.append(str(ctx.author.id))
    saveAll()
async def updateStatus():
    user = str(await client.fetch_user(currentStik))[:-5]
    await client.change_presence(activity=discord.Game(f'{user} has the talking stick'))
async def rollTalkingStick(ctx):
    global activeMemberIDs,activeMemberNames,currentStik,sticcs
    rand = activeMemberIDs[randint(0,len(activeMemberIDs)-1)]
    while rand == currentStik: rand = activeMemberIDs[randint(0,len(activeMemberIDs)-1)]; logEvent(ctx,'talking stick rerolled to same user, rerolling')
    newStik = await ctx.guild.fetch_member(rand)
    oldStik = await ctx.guild.fetch_member(currentStik)
    await oldStik.remove_roles(tsRole)
    await newStik.add_roles(tsRole)
    await client.get_channel(742239160399822868).send(f'congrats <@!{rand}>, you have the talking stick.')
    currentStik = rand
    sticcs.update({ctx.author.id:(sticcs[ctx.author.id])+1}) if ctx.author.id in sticcs else sticcs.update({ctx.author.id:1})
    activeMemberNames = []
    activeMemberIDs = []
    saveAll()
    logEvent(ctx,f'rerolled talking stick to {rand}')
@client.event
async def on_ready():
    log=f"the discipline sticc connected to Discord!"
    logging.warning(log)
    print(f'{log}\n')
    await updateStatus()
@client.event
async def on_message(message):
    try:
        if message.guild.id != serverId: return
    except:
        if message.channel.id == 820344365985038357: pass
        else: return
    if str(message.author.id) not in activeMemberIDs and str(message.author.id) not in bannedUsers: logEvent(message,f'adding {message.author.name} to active members',True); await activeMembers(message)
    if message.author.id == 713586207119900693 and datetime.today().weekday() in updateDays: await rollTalkingStick(message); await updateStatus()
    await client.process_commands(message)
@client.command(name='setDays')
async def setDays(ctx,*,arg):
    global updateDays
    if str(ctx.author.id) not in admins: print('failed to update reroll days - not admin'); await ctx.send(f'you have insufficient permissions.'); return
    updateDays.clear()
    if arg == 'everyday': updateDays = [0,1,2,3,4,5,6]; await ctx.send('done'); return
    if arg == 'none': updateDays = []; await ctx.send('done'); return
    days = arg.split(', ')
    for i in days: updateDays.append(daysConv[i])
    await ctx.send(f'done')
@client.command(name='rerollDays')
async def currentDays(ctx):
    currentDays = ''
    for i in updateDays: currentDays += f'{daysConvR[int(i)]} '
    await ctx.send(f'the current reroll days are {currentDays}')
@client.command(name='fReroll')
async def forceReroll(ctx):
    if str(ctx.author.id) in admins: await rollTalkingStick(ctx); await updateStatus(); logEvent(ctx,'force rerolling talking stick')
    else: logEvent(ctx,'failed talking stick reroll: user not an admin')
@client.command(name='listActive')
async def listActive(ctx):
    active = ''
    for i in activeMemberNames: active += f'{i}\n'
    await ctx.send(embed=discord.Embed(title='Active Users',description=active,color=ctx.author.color))
@client.command(name='removeActive')
async def removeActive(ctx,id):
    if str(ctx.author.id) not in admins: return
    if len(id) != 18: await ctx.send('id error'); return
    for i in range(len(activeMemberIDs)):
        if id == activeMemberIDs[i]: activeMemberIDs.pop(i); activeMemberNames.pop(i); await ctx.send('done'); return
    else: await ctx.send('user was not in active list')
@client.command(name='addActive')
async def addActive(ctx,id):
    if str(ctx.author.id) not in admins: return
    if len(id) != 18: await ctx.send('id error'); return
    if id in activeMemberIDs: await ctx.send('user is already active'); return
    activeMemberIDs.append(id)
    activeMemberNames.append(await ctx.guild.fetch_member(id))
    await ctx.send('done')
@client.command(name='leaderboard')
async def leaderboard(ctx):
    global idNameCache,sticcs
    sticcs = {key: value for key, value in sorted(sticcs.items(), key=lambda item: item[1],reverse=True)}
    response = ''
    index = 1
    for i in sticcs:
        if i in idNameCache: username = idNameCache[i]
        else:
            logEvent(ctx,f'adding {i} to ID cache')
            user = await client.fetch_user(i)
            idNameCache.update({i:user.name})
            username = idNameCache[i]
        rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
        response += f'{rank} - {username}: {sticcs[i]}\n'
    await ctx.send(embed=discord.Embed(title='sticc Leaderboard:',description=response,color=ctx.author.color))
    logEvent(ctx,'with sticc leaderboard',False,'r')
    saveAll()
@client.command(name='clearIDcache')
async def clearIDcache(ctx):
    global idNameCache
    if ctx.author.id not in admins: return
    idNameCache = {}
    logEvent(ctx,'cleared user ID cache')
    await ctx.send('done')
#help commands
@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(title='Help',description='sticc!help <command> for more info',color=ctx.author.color)
    embed.add_field(name='user commands',value='listActive\nrerollDays\nsticcLeaderboard')
    embed.add_field(name='admin commands',value='addActive\nclearIDcache\nfReroll\nremoveActive\nsetDays')
    await ctx.send(embed=embed)
@help.command(name='listActive')
async def help_listActive(ctx): await ctx.send(embed=discord.Embed(title='listActive',description='lists all users who are active enough to be rolled the talking sticc.',color=ctx.author.color).add_field(name='Syntax',value='sticc!listActive'))
@help.command(name='rerollDays')
async def help_rerollDays(ctx): await ctx.send(embed=discord.Embed(title='rerollDays',description='lists the days when the talking sticc will be rerolled.',color=ctx.author.color).add_field(name='Syntax',value='sticc!rerollDays'))
@help.command(name='addActive')
async def help_addActive(ctx): await ctx.send(embed=discord.Embed(title='addActive',description='manually adds a user to the list of active users.',color=ctx.author.color).add_field(name='Syntax',value='sticc!addActive <userID>'))
@help.command(name='fReroll')
async def help_fReroll(ctx): await ctx.send(embed=discord.Embed(title='fReroll',description='force rerolls the talking sticc, ignoring time and date.',color=ctx.author.color).add_field(name='Syntax',value='sticc!fReroll'))
@help.command(name='removeActive')
async def help_removeActive(ctx): await ctx.send(embed=discord.Embed(title='removeActive',description='manually removes a user from the list of active users.',color=ctx.author.color).add_field(name='Syntax',value='sticc!removeActive <userID>'))
@help.command(name='setDays')
async def help_setDays(ctx): await ctx.send(embed=discord.Embed(title='setDays',description='sets which days the talking sticc will reroll.',color=ctx.author.color).add_field(name='Syntax',value='sticc!setDays <everyday/none/day1, day2, day3 etc.>'))
@help.command(name='leaderboard')
async def help_leaderboard(ctx): await ctx.send(embed=discord.Embed(title='leaderboard',description='lists leaderboard for total number of times a user has recieved the talking sticc.',color=ctx.author.color).add_field(name='Syntax',value='sticc!leaderboard'))
@help.command(name='clearIDcache')
async def help_clearIDcache(ctx): await ctx.send(embed=discord.Embed(title='clearIDcache',description='clears the cache of ID and username links.',color=ctx.author.color).add_field(name='Syntax',value='sticc!clearIDcache'))
client.run(token)