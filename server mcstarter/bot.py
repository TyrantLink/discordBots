import os
import sys
import json
import logging
import discord
import requests
import subprocess
from time import sleep
from mcrcon import MCRcon
from pickle import load,dump
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands
from mcstatus import MinecraftServer

os.chdir(r'S:\ProgrammingProjects\&DiscordBots\server mcstarter')
logging.basicConfig(format='[%(asctime)s.%(msecs)03d] %(message)s',filename='output.log',level=logging.WARNING,datefmt='%d/%m/%Y %H:%M:%S')
load_dotenv()
saveFile = 'save.dat'
token=os.getenv('token')
serverQuery=os.getenv('serverQuery')
mcRconHost=os.getenv('mcRconHost')
mcRconPort=int(os.getenv('mcRconPort'))
mcRconPassword=os.getenv('mcRconPassword')
serverStarted = False
maxServerStartTime = 90
client = commands.Bot(command_prefix='mc!')
client.remove_command('help')
logModes = {'r':'responded ','s':'status changed to ','n':''}
admins = [250797109022818305]
moderators = [250797109022818305,434133025450754058,344912616629469184]
mc = MCRcon(mcRconHost,mcRconPassword,mcRconPort)
sizes = {0:'bytes',1:'KBs',2:'MBs',3:'GBs'}
bannedVariables = ['token','__file__','servers','']

unavailableReason = ''

with open('servers.json','r') as file: servers = json.loads(file.read())
with open('save.dat','rb') as save: bannedUsers = load(save)
def logEvent(ctx,text,mode='n'):
    try: m=logModes[mode]
    except: m='unknown log mode'
    log=f"{m}{text} in {ctx.guild} - {ctx.channel}"
    logging.warning(log)
    print(log)
def saveAll():
    with open('save.dat','wb') as save: dump(bannedUsers,save)
def getServerSize(server):
    size = 0; sizeType = 0; response = ''
    for path, dirs, files in os.walk(servers[server]['directory']):
        for f in files: fp = os.path.join(path, f); size += os.path.getsize(fp)
    while True:
        if size/1024 > 1: size = size/1024; sizeType += 1
        else: response = f'{round(size,3)} {sizes[sizeType]}'; dirs = dirs; break #fuck you debugger
    return response
async def pingServer(ctx):
    global serverStarted,mc
    try: MinecraftServer.lookup(serverQuery).query().players.online; serverStarted = True; await client.change_presence(activity=discord.Game('Server Started'))
    except: serverStarted = False; await client.change_presence(activity=discord.Game('Server Stopped')); return
async def permissionChecker(ctx,*args,server=None,id=None):
    for i in args:
        match i:
            case 'banned':
                if ctx.author.id in bannedUsers: await ctx.send('error: user is banned.'); return 'failed'
            case 'serverStarted':
                if serverStarted: await ctx.send(f'a server is already up.'); return 'failed'
            case 'serverName':
                if server=='': await ctx.send('unspecified server.'); await serverList(ctx); return 'failed'
            case 'serverStopped':
                if not serverStarted: await ctx.send('the server is not up.'); return 'failed'
            case 'admin':
                if ctx.author.id not in admins: await ctx.send('you do not have sufficient permissions.'); return 'failed'
            case 'moderator':
                if ctx.author.id not in moderators: await ctx.send('insufficient permissions.'); return 'failed'
            case 'id':
                if id=='': await ctx.send('unspecified user id.'); return 'failed'
                if len(id) != 18: await ctx.send('id error'); return 'failed'
            case 'serverExists':
                try: servers[server]
                except: await ctx.send('unknown server name.'); return 'failed'
@client.event
async def on_ready():
    log=f"{client.user.name} connected to Discord!"
    logging.warning(log)
    print(f'{log}\n')
    await client.change_presence(activity=discord.Game('Server Stopped'))
@client.event
async def on_message(message):
    if message.author == client.user: return
    await pingServer(message)
    await client.process_commands(message)
@client.command(name='start')
async def startServer(ctx,server=''):
    global serverStarted
    if unavailableReason != '': await ctx.send(f'sorry, starting servers is currently unavailable because: {reason}'); return
    if await permissionChecker(ctx,'banned','serverStarted','serverName','serverExists',server=server) == 'failed': return
    os.chdir(servers[server]['directory'])
    os.startfile('botStart.bat')
    serverStarted = True
    await client.change_presence(activity=discord.Game('Server Started'))
    await ctx.send('okay, it\'s starting.')
    logEvent(ctx,'starting server')
    loop = 0
    os.chdir(r'S:\ProgrammingProjects\&DiscordBots\server mcstarter')
    while True:
        if loop >= maxServerStartTime: await ctx.send('error starting server.'); return
        try: MinecraftServer.lookup(serverQuery).query().players.online; break
        except: sleep(1); loop += 1
    await ctx.send('it should be up')
@client.command(name='online')
async def onlinePlayers(ctx):
    if await permissionChecker(ctx,'banned') == 'failed': return
    try: players = MinecraftServer.lookup(serverQuery).query().players.names; pList = ''
    except: await ctx.send('cannot connect to server. is it online?'); return
    if players == []: await ctx.send('no one is online.'); return
    for i in players: pList += f'{i}\n'
    await ctx.send(embed=discord.Embed(title='Players Online:',description=pList,color=ctx.author.color))
@client.command(name='stop')
async def stopServer(ctx,mode=''):
    global serverStarted,mc
    if await permissionChecker(ctx,'banned','serverStopped') == 'failed': return
    while True:
        if ctx.author.id in admins and mode == '-f': break
        try:
            if MinecraftServer.lookup(serverQuery).query().players.online > 0: await ctx.send('no, fuck you, there are people online.'); return 'failed'
        except: break
    try: mc.connect(); mc.command('stop'); mc.disconnect(); serverStarted = False; await client.change_presence(activity=discord.Game('Server Stopped')); print('rcon stop command')
    except: await ctx.send('failed to shutdown server.'); return 'failed'
    await ctx.send('stopping server')
    while True:
        sleep(1)
        try: MinecraftServer.lookup(serverQuery).query().players.online; continue
        except: break
    await ctx.send('server stopped.')
@client.command(name='servers')
async def serverList(ctx):
    if await permissionChecker(ctx,'banned') == 'failed': return
    serverList = ''
    for i in servers: serverList += f'{i}\n'
    await ctx.send(embed=discord.Embed(title='Servers:',description=serverList,color=ctx.author.color))
@client.command(name='info')
async def info(ctx,server=''):
    if await permissionChecker(ctx,'banned','serverName','serverExists',server=server) == 'failed': return
    response=''
    for i in servers[server]:
        if i=='directory' or i=='isModded' or i=='mods': continue
        response += f'{i}: {servers[server][i]}\n'
    response += 'modpack:\nvanilla\n' if servers[server]['isModded']=='no' else f'modpack:\nhttps://mods.nutt.dev/{server}\n'
    response += f'size: {getServerSize(server)}'
    logEvent(ctx,f'with server info for {server}','r')
    await ctx.send(embed=discord.Embed(title=f'{server} info:',description=response,color=ctx.author.color))
@client.command(name='nugget')
async def nugget(ctx):
    if await permissionChecker(ctx,'banned') == 'failed': return
    await ctx.send('https://media.discordapp.net/attachments/815766553978863626/825913334817095710/iu.png?width=1641&height=864')
@client.command(name='cmd')
async def sendCommand(ctx,*cmd):
    if await permissionChecker(ctx,'banned','admin') == 'failed': return
    command = ''
    for i in cmd: command += f'{i} '
    command = command[:-1]
    try: mc.connect(); response = mc.command(command); mc.disconnect(); print('rcon cmd command')
    except: await ctx.send('failed to send command'); return
    try: await ctx.send(response)
    except: pass
@client.command(name='reload')
async def reloadData(ctx):
    global servers,token,serverQuery,mcRconHost,mcRconPort,mcRconPassword
    if await permissionChecker(ctx,'banned','admin') == 'failed': return
    with open('servers.json','r') as file: servers = json.loads(file.read())
    load_dotenv()
    token=os.getenv('token')
    serverQuery=os.getenv('serverQuery')
    mcRconHost=os.getenv('mcRconHost')
    mcRconPort=int(os.getenv('mcRconPort'))
    mcRconPassword=os.getenv('mcRconPassword')
    await ctx.send('successfully reloaded.')
@client.command(name='ban')
async def ban(ctx,id=''):
    if await permissionChecker(ctx,'banned','moderator','id',id=id) == 'failed': return
    bannedUsers.append(id)
    saveAll()
    await ctx.send('done.')
@client.command(name='unban')
async def unban(ctx,id):
    if await permissionChecker(ctx,'banned','moderator','id',id=id) == 'failed': return
    bannedUsers.remove(id)
    saveAll()
    await ctx.send('done.')
@client.command(name='bannedList')
async def bannedList(ctx):
    if await permissionChecker(ctx,'banned') == 'failed': return
    response = ''
    for i in bannedUsers: response += f'{await client.fetch_user(i)}\n'
    if response == '': await ctx.send('no users are banned.'); return
    await ctx.send(embed=discord.Embed(title='Banned Users:',description=response,color=ctx.author.color))
@client.command(name='modList')
async def modList(ctx,server=''):
    if await permissionChecker(ctx,'banned','serverName','serverExists',server=server) == 'failed': return
    response = servers[server]['mods'][0]
    for i in range(1,len(json['mods'])): response+=f'\n{json["mods"][i]}'
    if len(response) >= 2000: response = 'it\'s too long for the discord character limit so you have to google it fuck you.'
    await ctx.send(embed=discord.Embed(title=f'{server} mods:',description=response,color=ctx.author.color))
@client.command(name='restart')
async def restart(ctx,server='',mode=''):
    if await permissionChecker(ctx,'banned','serverName','serverExists',server=server) == 'failed': return
    if await stopServer(ctx,mode) == 'failed': return
    await startServer(ctx,server)
"""
I FUCKING GIVE UP.
@client.command(name='set')
async def setVariable(ctx,variable,*values):
    if await permissionChecker(ctx,'admin') == 'failed': return
    print(type(variable))
    try: variable = globals()[variable]
    except: await ctx.send('unknown variable name.'); return
    print(type(variable))
    value = ''
    for i in values: value += f'{i} '
    print(value)
    globals()[variable] = value
    await ctx.send('done')
    await get(ctx,variable)
"""
@client.command(name='get')
async def get(ctx,variable=''):
    if variable=='': await ctx.send('unspecified variable.'); return
    if variable in bannedVariables: await ctx.send('no, fuck you.'); return
    if ctx.author.id not in moderators: return
    try: variable = globals()[variable]
    except: await ctx.send('unknown variable name.'); return
    await ctx.send(f'```{variable}```')
#help commands
@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(title='Help',description='mc!help <command> for more info',color=ctx.author.color)
    embed.add_field(name='user commands',value='help\ninfo\nmodList\nnugget\nonline\nrestart\nservers\nstart\nstop')
    embed.add_field(name='admin commands',value='ban\nbannedList\ncmd\nreload\nunban')
    await ctx.send(embed=embed)
@help.command(name='reload')
async def help_reload(ctx): await ctx.send(embed=discord.Embed(title='reload',description='reloads `servers.json` and `.env` files.',color=ctx.author.color).add_field(name='Syntax',value='mc!reload'))
@help.command(name='cmd')
async def help_cmd(ctx): await ctx.send(embed=discord.Embed(title='cmd',description='runs a command on current minecraft server.',color=ctx.author.color).add_field(name='Syntax',value='mc!cmd <command> [arguments]'))
@help.command(name='ban')
async def help_ban(ctx): await ctx.send(embed=discord.Embed(title='ban',description='bans a user from interacting with the bot, with the exeption of mc!help commands.',color=ctx.author.color).add_field(name='Syntax',value='mc!ban <userID>'))
@help.command(name='bannedList')
async def help_bannedList(ctx): await ctx.send(embed=discord.Embed(title='bannedList',description='lists all banned users.',color=ctx.author.color).add_field(name='Syntax',value='mc!bannedList'))
@help.command(name='unban')
async def help_unban(ctx): await ctx.send(embed=discord.Embed(title='unban',description='unbans a user from interacting with the bot.',color=ctx.author.color).add_field(name='Syntax',value='mc!unban <userID>'))
@help.command(name='help')
async def help_help(ctx): await ctx.send(embed=discord.Embed(title='help',description='what the fuck do you think you\'re doing?',color=ctx.author.color).add_field(name='Syntax',value='mc!help <command>'))
@help.command(name='info')
async def help_info(ctx): await ctx.send(embed=discord.Embed(title='info',description='lists all information for given server.',color=ctx.author.color).add_field(name='Syntax',value='mc!info <server>'))
@help.command(name='modList')
async def help_modList(ctx): await ctx.send(embed=discord.Embed(title='modList',description='lists all mods for given server.',color=ctx.author.color).add_field(name='Syntax',value='mc!modList <server>'))
@help.command(name='nugget')
async def help_nugget(ctx): await ctx.send(embed=discord.Embed(title='nugget',description='nugget',color=ctx.author.color).add_field(name='Syntax',value='mc!nugget'))
@help.command(name='online')
async def help_online(ctx): await ctx.send(embed=discord.Embed(title='online',description='lists the players who are online.',color=ctx.author.color).add_field(name='Syntax',value='mc!online'))
@help.command(name='restart')
async def help_restart(ctx): await ctx.send(embed=discord.Embed(title='restart',description='stops current server then starts given server.',color=ctx.author.color).add_field(name='Syntax',value='mc!restart <server>'))
@help.command(name='servers')
async def help_servers(ctx): await ctx.send(embed=discord.Embed(title='servers',description='lists all servers available.',color=ctx.author.color).add_field(name='Syntax',value='mc!servers'))
@help.command(name='start')
async def help_start(ctx): await ctx.send(embed=discord.Embed(title='start',description='starts a minecraft server.',color=ctx.author.color).add_field(name='Syntax',value='mc!start <server>'))
@help.command(name='stop')
async def help_stop(ctx): await ctx.send(embed=discord.Embed(title='stop',description='stops the current minecraft server if there are no players online.',color=ctx.author.color).add_field(name='Syntax',value='mc!stop [mode]'))
client.run(token)
