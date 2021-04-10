import os
import json
import shutil
import logging
import discord
from time import time
from NHentai import NHentai
from pickle import load,dump
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

#settings
msgToConsole = True


def setupLogger(name,log_file,level=logging.WARNING):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s','%d/%m/%Y %H:%M:%S')
    fileHandler = logging.FileHandler(log_file, mode='a',encoding='utf-8')
    fileHandler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(fileHandler)
    return logger
#startup
os.chdir(r'S:\ProgrammingProjects\&DiscordBots\the mcfuck')
load_dotenv()
token=os.getenv('token') 
outputLog = setupLogger('output log','logs/output.log')
sentLog = setupLogger('sent log','logs/messages/sent.log')
editedLog = setupLogger('edited log','logs/messages/edited.log')
deletedLog = setupLogger('deleted log','logs/messages/deleted.log')
client = commands.Bot(command_prefix='mcfuck!')
client.remove_command('help')
logModes = {'r':'responded ','s':'status changed to ','n':''}
hentaiLanguages = {'e':'english','j':'japanese','c':'chinese'}
admins = [250797109022818305]
moderators = [250797109022818305,181824790078685184,645069774438531089]
bannedVariables = ['token','__file__','qa','userqa','godqa']
nhentai = NHentai()
godExempt = True
with open('qa.json','r') as qaFile: qa = json.loads(qaFile.read()); userqa = qa['userqa']; godqa = qa['godqa']
with open('save.dat','rb') as save:
    messages = load(save)
    foundstuffs = load(save)
    idNameCache = load(save)
for i in range(len(userqa)): 
    try: foundstuffs[i]
    except: foundstuffs.append(0)
def saveAll():
    with open('save.dat','wb') as save:
        dump(messages,save)
        dump(foundstuffs,save)
        dump(idNameCache,save)
def logEvent(ctx,text,mode='n'):
    try: m=logModes[mode]
    except: m='unknown log mode'
    log=f"{m}{text} in {ctx.guild} - {ctx.channel}"
    outputLog.warning(log)
    print(log)
def logMessages(ctx,type,ctx2='',ext=''):
    modColors = '\033[92m' if ctx.author.id in moderators else '\033[0m'
    colorReset = '\033[0m'
    match type:
        case 's':
            log=f'{ctx.author} sent "{ctx.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
            if msgToConsole and not ctx.author.bot and '' not in ctx.content: print(f'{ctx.author} sent "{modColors}{ctx.content}{colorReset}" in {ctx.channel}{colorReset}')
            sentLog.warning(log)
        case 'd':
            log=f'"{ctx.content}" by {ctx.author} was deleted in {"" if ctx.guild == None else f"{ctx.guild} - "} - {ctx.channel}{ext}'
            if msgToConsole and '' not in ctx.content: print(f'"{modColors}{ctx.content}{colorReset}" by {ctx.author} was deleted in {ctx.channel}{colorReset}')
            deletedLog.warning(log)
        case 'e':
            log=f'{ctx.author} edited "{ctx.content}" into "{ctx2.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "} - {ctx.channel}{ext}'
            if msgToConsole and '' not in ctx.content: print(f'{ctx.author} edited "{modColors}{ctx.content}{colorReset}" into "{modColors}{ctx2.content}{colorReset}" in {ctx.channel}{colorReset}')
            editedLog.warning(log)
def messageCount(ctx):
    userID = str(ctx.author.id)
    messages.update({userID:(messages[userID])+1}) if userID in messages else messages.update({userID:1})
    saveAll()
def messageBackup():
    shutil.copytree(f'{os.getcwd()}\\logs', f'{os.getcwd()}\\backups\\logs\\{datetime.fromtimestamp(time()).strftime("%d.%m.%Y %H.%M.%S")}')
async def autoResponse(ctx):
    global godExempt
    if ctx.author.bot: return
    if ctx.author.id == 250797109022818305:
        if ctx.content in godqa: await ctx.channel.send(godqa[ctx.content]); logEvent(ctx,godqa[ctx.content],'r')
        if ctx.content in userqa and godExempt == False: await ctx.channel.send(userqa[ctx.content]); logEvent(ctx,userqa[ctx.content],'r')
    else:
        if ctx.content in userqa:
            await ctx.channel.send(userqa[ctx.content]); logEvent(ctx,userqa[ctx.content],'r')
            for i in range(len(userqa)):
                if ctx.content == i:
                    if foundstuffs[i] == 0: foundstuffs[i] = 1; await ctx.channel.send('NEW AUTO RESPONSE FOUND'); saveAll()
@client.event
async def on_ready():
    outputLog.warning(f"{client.user.name} connected to Discord!")
    print(f"{client.user.name} connected to Discord!\n")
@client.event
async def on_message(message):
    logMessages(message,'s',' - image or embed') if message.content == "" else logMessages(message,'s')
    if message.author.id == 713586207119900693: messageBackup()
    if message.author.bot: return
    await autoResponse(message)
    messageCount(message)
    await client.process_commands(message)
@client.event
async def on_message_delete(message):
    logMessages(message,'d',' - image or embed') if message.content == "" else logMessages(message,'d')
@client.event
async def on_message_edit(message_before,message_after):
    logMessages(message_before,'e',message_after,' - image or embed') if message_after.content == "" else logMessages(message_before,'e',message_after)
@client.command(name='messageLeaderboard')
async def messageLeaderboard(ctx):
    global idNameCache,messages
    messages = {key: value for key, value in sorted(messages.items(), key=lambda item: item[1],reverse=True)}
    response = ''
    username = ''
    index = 1
    for i in messages:
        if i in idNameCache: username = idNameCache[i]
        else:
            logEvent(ctx,f'adding {i} to ID cache')
            user = await client.fetch_user(i)
            idNameCache.update({i:user.name})
            username = idNameCache[i]
        rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
        response += f'{rank} - {username}: {messages[i]}\n'
    await ctx.send(embed=discord.Embed(title='Message Leaderboard:',description=response,color=ctx.author.color))
    logEvent(ctx,'with message leaderboard','r')
    saveAll()
@client.command(name='clearIDcache')
async def clearIDcache(ctx):
    global idNameCache
    if ctx.author.id not in admins: return
    idNameCache = {}
    logEvent(ctx,'cleared user ID cache')
    await ctx.send('done')
@client.command(name='godExempt')
async def exemptGod(ctx,arg=not godExempt): 
    global godExempt
    if ctx.author.id != 250797109022818305: return
    try: bool(arg)
    except: return
    godExempt = arg
    await ctx.send('alright')
@client.command(name='hentai')
async def hentai(ctx,id=''):
    if id != '': await ctx.send(f'https://nhentai.net/g/{id}')
    else: await ctx.send(f'https://nhentai.net/g/{nhentai.get_random().id}')
@client.command(name='get')
async def get(ctx,variable=''):
    if variable=='': await ctx.send('unspecified variable.'); return
    if variable in bannedVariables: await ctx.send('no, fuck you.'); return
    if ctx.author.id not in moderators: return
    try: variable = globals()[variable]
    except: await ctx.send('unknown variable name.'); return
    await ctx.send(f'```{variable}```')
@client.command(name='messageBackup')
async def messageBackupcmd(ctx):
    messageBackup()
    await ctx.send('done')
#help commands
@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(title='Help',description='mcfuck!help <command> for more info',color=ctx.author.color)
    embed.add_field(name='user commands',value='hentai\nmessageLeaderboard')
    embed.add_field(name='admin commands',value='clearIDcache\nget\ngodExempt')
    await ctx.send(embed=embed)
@help.command(name='hentai')
async def help_hentai(ctx): await ctx.send(embed=discord.Embed(title='hentai',description='give random hentai or give sauce from id.',color=ctx.author.color).add_field(name='Syntax',value='mcfuck!hentai [id]'))
@help.command(name='messageLeaderboard')
async def help_messageLeaderboard(ctx): await ctx.send(embed=discord.Embed(title='messageLeaderboard',description='lists leaderboard for total messages sent by users.',color=ctx.author.color).add_field(name='Syntax',value='mcfuck!messageLeaderboard'))
@help.command(name='clearIDcache')
async def help_clearIDcache(ctx): await ctx.send(embed=discord.Embed(title='clearIDcache',description='clears the cache of ID and username links.',color=ctx.author.color).add_field(name='Syntax',value='mcfuck!clearIDcache'))
@help.command(name='get')
async def help_get(ctx): await ctx.send(embed= discord.Embed(title='get',description='prints out given variable.',color=ctx.author.color).add_field(name='Syntax',value='mcfuck!get <variable>'))
@help.command(name='godExempt')
async def help_godExempt(ctx): await ctx.send(embed= discord.Embed(title='godExempt',description='toggles or sets if bot will auto respond to god messages.',color=ctx.author.color).add_field(name='Syntax',value='mcfuck!godExempt [bool]'))
client.run(token)
