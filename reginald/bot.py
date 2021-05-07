import os,re,json,logging,discord,requests,asyncio
from mcrcon import MCRcon
from random import randint
from shutil import copytree
from time import time,sleep
from pickle import load,dump
from datetime import datetime
from dotenv import load_dotenv
from mcstatus import MinecraftServer
from discord.ext import commands,tasks
# from serverConnection import client
from discord_slash import cog_ext,SlashCommand,SlashContext
from discord.ext.commands import has_permissions,MissingPermissions,is_owner



def setupLogger(name,log_file,level=logging.WARNING):
  logger = logging.getLogger(name)
  formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s','%d/%m/%Y %H:%M:%S')
  fileHandler = logging.FileHandler(log_file, mode='a',encoding='utf-8')
  fileHandler.setFormatter(formatter)
  logger.setLevel(level)
  logger.addHandler(fileHandler)
  return logger
os.chdir(r'S:\ProgrammingProjects\&DiscordBots\reginald')
load_dotenv()
with open('save.json','r') as save: saveLoad = json.loads(save.read())
configVariables = saveLoad['config']
dynamicVariables = saveLoad['dynamic']
staticVariables = {
  'serverStarted':False,
  'sizes':{2:'MBs',3:'GBs'},
  'token':os.getenv('token'),
  'mcRconHost':os.getenv('mcRconHost'),
  'hypixelKey':os.getenv('hypixelKey'),
  'serverQuery':os.getenv('serverQuery'), 
  'mcRconPort':int(os.getenv('mcRconPort')),
  'mcRconPassword':os.getenv('mcRconPassword'),
  'outputLog':setupLogger('output log','logs/output.log'),
  'sentLog':setupLogger('sent log','logs/messages/sent.log'),
  'editedLog':setupLogger('edited log','logs/messages/edited.log'),
  'deletedLog':setupLogger('deleted log','logs/messages/deleted.log'),
  'valueConverter':{'True':True,'False':False,'true':True,'false':False},
  'bannedVariables':['token','__file__','qa','userqa','godqa','hypixelKey','servers'],
  'client':commands.Bot(command_prefix=('reginald!','reg!','r!'),case_insensitive=True,help_command=None,owner_id=int(os.getenv('ownerID')))
  }
qa = json.loads(open('qa.json','r').read()); userqa = qa['userqa']; godqa = qa['godqa']
servers = json.loads(open('servers.json','r').read())
for var in dynamicVariables: globals()[var] = dynamicVariables[var]
for var in staticVariables: globals()[var] = staticVariables[var]
for var in configVariables: globals()[var] = configVariables[var]
async def sticcLoad():
  for guild in dynamicVariables[sticcServers]:
    globals()['tsRoles'].update({guild:{tsRole:discord.Object(guild['tsRole'])}})
    globals()['tsChannels'].update({guild:{tsChannel:await client.fetch_channel(guild['tsChannel'])}})

slash = SlashCommand(client)
mc = MCRcon(mcRconHost,mcRconPassword,mcRconPort)

def adminOrOwner(): return (is_owner() or has_permissions(administrator=True))
def modOrOwner(): return (is_owner() or has_permissions(manage_server=True))
def save(): json.dump({'config':configVariables,'dynamic':dynamicVariables},open('save.json','w+'),indent=2)

class serverMcstarter(commands.Cog):
  def __init__(self,client): self.client = client
  @cog_ext.cog_subcommand(base='minecraft',name='start',description='starts a minecraft server.')
  async def start(self,ctx:SlashContext,server):
    try: os.chdir(servers[server]['directory'])
    except: await ctx.send('server name error')
    if serverStarted: return
    os.startfile('botStart.bat')
    os.chdir(r'S:\ProgrammingProjects\&DiscordBots\reginald')
    await ctx.send('okay, it\'s starting.')
    for i in range(maxServerStartTime):
      try: MinecraftServer.lookup(serverQuery).query().players.online; break
      except: sleep(1)
    else: await ctx.send('error starting server.'); return
    await ctx.send('it should be up.')
  @cog_ext.cog_subcommand(base='minecraft',name='stop',description='stops active minecraft server.')
  async def stop(self,ctx:SlashContext,args=None):
    if args == '-f' and not adminOrOwner():
      if MinecraftServer.lookup(serverQuery).query().players.online > 0: await ctx.send('no, fuck you, there are people online.'); return False
    try: mc.connect(); mc.command('stop'); mc.disconnect(); serverStarted = False; await client.change_presence(activity=discord.Game('Server Stopped')); await ctx.send('stopping server.')
    except: await ctx.send('failed to shutdown server.'); return False
  @cog_ext.cog_subcommand(base='minecraft',name='cmd',description='runs command on the active minecraft server.')
  @is_owner()
  async def cmd(self,ctx:SlashContext,command):
    try: mc.connect(); response = mc.command(command); mc.disconnect()
    except: await ctx.send('failed to send command'); return
    try: await ctx.send(response)
    except: pass
  @cog_ext.cog_subcommand(base='minecraft',name='info',description='lists info on given minecraft server.')
  async def list_info(self,ctx:SlashContext,server):
    info = []
    try:
      for i in servers[server]:
        if i=='directory' or i=='isModded' or i=='mods': continue
        info.append(f'{i}: {servers[server][i]}')
    except: await ctx.send('server name error')
    info.append('modpack: vanilla') if servers[server]['isModded']=='no' else info.append(f'modpack: https://mods.nutt.dev/{server}')
    info.append(f'size: {nonAsync.getServerSize(server)}')
    await ctx.send(embed=discord.Embed(title=f'{server} info:',description='\n'.join(info),color=0x69ff69))
  @cog_ext.cog_subcommand(base='minecraft',name='online',description='returns list of players online.')
  async def online(self,ctx:SlashContext):
    try: players = MinecraftServer.lookup(serverQuery).query().players.names
    except: await ctx.send('cannot connect to server. is it online?'); return
    if players == []: await ctx.send('no one is online.'); return
    await ctx.send(embed=discord.Embed(title='Players Online:',description='\n'.join(players),color=0x69ff69))
  @cog_ext.cog_subcommand(base='minecraft',name='servers',description='lists all minecraft servers')
  async def list_servers(self,ctx:SlashContext): await ctx.send(embed=discord.Embed(title='Minecraft Servers:',description='\n'.join(servers),color=0x69ff69))
class theDisciplineSticc(commands.Cog):
  def __init__(self,client): self.client = client
  async def sticcLoop():
    await client.wait_until_ready()
    while client.is_ready:
        await asyncio.sleep(60)
        if datetime.now().strftime("%H:%M") == '09:00':
          try:
            for guild in dynamicVariables['sticcServers']: await general.rollTalkingStick(guild)
          except: await (discord.utils.get(guild.channels,name='general')).send('error: talking stick has not been set up in this server.')
          nonAsync.messageBackup()
  @cog_ext.cog_subcommand(base='sticc',name='setup',description='setup the discipline sticc.')
  @adminOrOwner()
  async def setup(self,ctx:SlashContext,role:discord.Role,channel:discord.TextChannel):
    tsRole = role; tsChannel = channel
    dynamicVariables.update({'sticcServers':{ctx.guild_id:{'tsRole':tsRole.id,'tsChannel':tsChannel.id}}})
    await ctx.send(embed=discord.Embed(title='Setup Complete.',description=f'role: <@&{tsRole.id}>\n\nchannel: <#{tsChannel.id}>',color=0x69ff69))
  @cog_ext.cog_subcommand(base='sticc',name='reroll',description='reroll the talking sticc')
  @adminOrOwner()
  async def reroll(self,ctx:SlashContext): await general.rollTalkingStick(ctx.guild.id)
  @cog_ext.cog_subcommand(base='leaderboard',name='sticcs',description='leaderboard of how many times someone has had the talking sticc')
  async def leaderboard_sticcs(self,ctx:SlashContext):
    names = []
    for member in dynamicVariables['sticcServers'][str(ctx.guild.id)]['sticcs']:
      if member not in idNameCache: idNameCache.update({member:(await client.fetch_user(member)).name})
      names.append(idNameCache[member])
    await ctx.send(embed=discord.Embed(title='Minecraft Servers:',description='\n'.join(names),color=0x69ff69))
  @cog_ext.cog_subcommand(base='sticc',name='active',description='lists members who have been active in the past day.')
  async def list_active(self,ctx:SlashContext):
    active = []
    for member in dynamicVariables['sticcServers'][str(ctx.guild.id)]['activeMembers']:
      if member not in idNameCache: idNameCache.update({member:(await client.fetch_user(member)).name})
      active.append(idNameCache[member])
    await ctx.send(embed=discord.Embed(title='Active Members:',description='\n'.join(active),color=0x69ff69))
class command(commands.Cog):
  global godExempt
  def __init__(self,client): self.client = client
  @cog_ext.cog_subcommand(base='hello',name='reginald',description='have reginald say hi.')
  async def hello_reginald(self,ctx:SlashContext): await ctx.send(file=discord.File('reginald.png'))
  @cog_ext.cog_slash(name='clearidcache',description='clears ID cache variable')
  @is_owner()
  async def clearIDcache(self,ctx:SlashContext):
    idNameCache = []; await ctx.send('successfully cleared ID cache')
  @cog_ext.cog_slash(name='config',description='set variables for the bot')
  @is_owner()
  async def config(self,ctx:SlashContext,variable,value):
    if variable not in configVariables: await ctx.send('variable error'); return
    realVar = globals()[variable]
    if value in valueConverter and type(realVar) == bool: value = valueConverter[value]
    else:
      try: value = int(value)
      except: await ctx.send('value error'); return
    if type(realVar) == type(value): globals()[variable] = value
    else: await ctx.send('type error'); return
    await ctx.send(f'successfully set {variable} to {globals()[variable]}')
  @cog_ext.cog_slash(name='reload',description='reloads save files')
  @is_owner()
  async def reloadSaves(self,ctx:SlashContext):
    qa = json.loads(open('qa.json','r').read()); userqa = qa['userqa']; godqa = qa['godqa']
    servers = json.loads(open('servers.json','r').read())
    configVariables = saveLoad['config']
    dynamicVariables = saveLoad['dynamic']
    for var in dynamicVariables: globals()[var] = dynamicVariables[var]
    for var in staticVariables: globals()[var] = staticVariables[var]
    for var in configVariables: globals()[var] = configVariables[var]
    await ctx.send('reload successful.')
  @cog_ext.cog_subcommand(base='list',name='config',description='list config variables.')
  async def list_config(self,ctx:SlashContext):
    config = []
    for i in configVariables: config.append(f'{i}:{configVariables[i]}')
    await ctx.send(embed=discord.Embed(title='Config:',description='\n'.join(config),color=0x69ff69))
  @cog_ext.cog_slash(name='exec',description='execute any python command on host computer.')
  @is_owner()
  async def execCMD(ctx,*Command):
    try: await ctx.send(eval(' '.join(Command)))
    except Exception as e: await ctx.send(e)
  @cog_ext.cog_slash(name='roll',description='roll with modifiers')
  async def roll(self,ctx:SlashContext,dice:int,sides:int,modifiers:int):
    if dice > maxRoll or sides > maxRoll or dice < 0 or sides < 0: await ctx.send(f'rolls must be between 0 and {maxRoll}!')
    result = modifiers
    rolls = []
    for i in range(dice): roll = randint(1,sides); rolls.append(roll); result+=roll
    try: await ctx.send(embed=discord.Embed(title='rolls:',description=','.join(rolls),color=0x69ff69).add_field(name='Result:',value=result))
    except: await ctx.send(embed=discord.Embed(title='rolls:',description='total rolls above character limit.',color=0x69ff69).add_field(name='Result:',value=result))
  @cog_ext.cog_subcommand(base='leaderboard',name='messages',description='leaderboard of total messages sent.')
  async def leaderboard_messages(self,ctx:SlashContext):
    dynamicVariables['messages'] = {key: value for key, value in sorted(dynamicVariables['messages'].items(), key=lambda item: item[1],reverse=True)}
    names = []
    index = 1
    for member in dynamicVariables['messages']:
      if member not in idNameCache: idNameCache.update({member:(await client.fetch_user(member)).name})
      rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
      names.append(f'{rank} - {idNameCache[member]}: {dynamicVariables["messages"][member]}')
    await ctx.send(embed=discord.Embed(title='Messages:',description='\n'.join(names),color=0x69ff69))
  @cog_ext.cog_subcommand(base='get',name='avatar',description='returns the avatar of given user')
  async def get_avatar(self,ctx:SlashContext,user:discord.User,resolution=512): await ctx.send(str(user.avatar_url_as(format="png",size=resolution)))
  @cog_ext.cog_subcommand(base='get',name='guild',description='returns guild name from id')
  async def get_guild(self,ctx:SlashContext,guild): await ctx.send((await client.fetch_guild(int(guild))).name)
  @cog_ext.cog_subcommand(base='get',name='name',description='returns user name from id')
  async def get_name(self,ctx:SlashContext,user): await ctx.send((await client.fetch_user(int(user)).name))
  @cog_ext.cog_subcommand(base='get',name='variable',description='returns variable')
  @is_owner()
  async def get_variable(self,ctx:SlashContext,variable:str):
    if variable in bannedVariables: await ctx.send('no, fuck you.'); return
    try: variable = globals()[variable]
    except: await ctx.send('unknown variable name.'); return
    await ctx.send(f'```{type(variable)}\n{variable}```')
class msgLogger(commands.Cog):
  def __init__(self,client): self.client = client
  @commands.Cog.listener()
  async def on_message(self,message):
    nonAsync.logMessages(message,'s',' - image or embed') if message.content == "" else nonAsync.logMessages(message,'s')
    nonAsync.messageCount(message)
  @commands.Cog.listener()
  async def on_message_delete(self,message):
    if message.author == client.user and re.sub('​','',message.content) in userqa:
      while True:
        try: await message.channel.send(message.content); break
        except: sleep(0.1)
    nonAsync.logMessages(message,'d',' - image or embed') if message.content == "" else nonAsync.logMessages(message,'d')
  @commands.Cog.listener()
  async def on_bulk_message_delete(self,messages):
    for message in messages: nonAsync.logMessages(message,'bd',' - image or embed') if message.content == "" else nonAsync.logMessages(message,'bd')
  @commands.Cog.listener()
  async def on_message_edit(self,message_before,message_after):
    nonAsync.logMessages(message_before,'e',message_after,' - image or embed') if message_after.content == "" else nonAsync.logMessages(message_before,'e',message_after)
class nonAsync(commands.Cog):
  def __init__(self,client): self.client = client
  def messageCount(ctx):
    userID = str(ctx.author.id)
    guildID = str(ctx.guild.id)
    messages.update({userID:(messages[userID])+1}) if userID in messages else messages.update({userID:1})
    if userID not in dynamicVariables['sticcServers'][guildID]['activeMembers']:
      dynamicVariables['sticcServers'][guildID]['activeMembers'].append(userID)
      dynamicVariables.update({'sticcServers':{guildID:{'activeMembers':dynamicVariables['sticcServers'][guildID]['activeMembers']}}})
    save()
  def logMessages(ctx,type,ctx2='',ext=''):
    match type:
      case 's':
        log=f'{ctx.author} sent "{ctx.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
        if msgToConsole and not ctx.author.bot and '' not in ctx.content: print(f'{ctx.author} sent "{ctx.content}" in {ctx.channel}')
        sentLog.warning(log)
      case 'd':
        log=f'"{ctx.content}" by {ctx.author} was deleted in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
        if msgToConsole and '' not in ctx.content: print(f'"{ctx.content}" by {ctx.author} was deleted in {ctx.channel}')
        deletedLog.warning(log)
      case 'bd':
        log=f'"{ctx.content}" by {ctx.author} was purged in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
        if msgToConsole and '' not in ctx.content: print(f'"{ctx.content}" by {ctx.author} was purged in {ctx.channel}')
        deletedLog.warning(log)
      case 'e':
        if ctx.content == ctx2.content: return
        log=f'{ctx.author} edited "{ctx.content}" into "{ctx2.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
        if msgToConsole and '' not in ctx.content: print(f'{ctx.author} edited "{ctx.content}" into "{ctx2.content}" in {ctx.channel}')
        editedLog.warning(log)
  def messageBackup(): copytree(f'{os.getcwd()}\\logs', f'{os.getcwd()}\\backups\\logs\\{datetime.fromtimestamp(time()).strftime("%d.%m.%Y %H.%M.%S")}')
  def getServerSize(server):
    size = 0; sizeType = 0
    for path, dirs, files in os.walk(servers[server]['directory']):
      for f in files: fp = os.path.join(path, f); size += os.path.getsize(fp)
    while size/1024 > 1: size = size/1024; sizeType += 1
    return f'{round(size,3)} {sizes[sizeType]}'
class general(commands.Cog):
  def __init__(self,client): self.client = client
  @commands.Cog.listener()
  async def on_ready(self):
    outputLog.warning(f"{client.user.name} connected to Discord!")
    print(f"{client.user.name} connected to Discord!\n")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name='the collective one.'))
    await slash.sync_all_commands()
  @commands.Cog.listener()
  async def on_guild_join(self,guild): await (discord.utils.get(guild.channels,name='general')).send(file=discord.File('reginald.png'))
  @commands.Cog.listener()
  async def on_message(self,message):
    if message.author.bot: return
    globals()['lastChannel'] = message.channel
    if enableAutoResponses: await general.autoResponse(message)
  async def autoResponse(ctx):
    if ctx.author.bot: return
    if ctx.author.id == client.owner_id and ctx.content in userqa and not godExempt: await ctx.channel.send(userqa[ctx.content]); return
    if ctx.author.id != client.owner_id and ctx.content in userqa: await ctx.channel.send(userqa[ctx.content]); return
    if ctx.author.id == client.owner_id and ctx.content in godqa: await ctx.channel.send(godqa[ctx.content]); return
  async def rollTalkingStick(guild_id):
    sticcs = dynamicVariables['sticcServers'][str(ctx.guild.id)]['sticcs']
    rand = dynamicVariables['sticcServers'][guild_id]['activeMembers'][randint(0,len(dynamicVariables['sticcServers'][guild_id]['activeMembers'])-1)]
    oldStik = await server.fetch_member(currentStik)
    newStik = await server.fetch_member(rand)
    while rand == currentStik or (newStik.bot and oldStik.bot):
      rand = dynamicVariables['sticcServers'][guild_id]['activeMembers'][randint(0,len(dynamicVariables['sticcServers'][guild_id]['activeMembers'])-1)]
      oldStik = await server.fetch_member(currentStik)
      newStik = await server.fetch_member(rand)
    await oldStik.remove_roles(tsRole)
    await newStik.add_roles(tsRole)
    await tsChannel.send(f'congrats <@!{rand}>, you have the talking stick.')
    currentStik = rand
    sticcs.update({currentStik:(sticcs[currentStik])+1}) if currentStik in sticcs else sticcs.update({currentStik:1})
    dynamicVariables['sticcServers'][str(ctx.guild.id)]['activeMembers'] = []
    save()
@client.command(name='help')
async def redirectToSlash(ctx): await ctx.send('all commands have been ported to slash commands, type "/" to see a list of commands.')
@client.event
async def on_command_error(ctx,error): await ctx.send(f'error: {error}'); pass

async def sendMessage():
  await client.wait_until_ready()
  while client.is_ready:
    msg = input('message: ')
    await lastChannel.send(msg)


# client.loop.create_task(theDisciplineSticc.sticcLoop())
# client.add_cog(theDisciplineSticc(client))
# client.loop.create_task(sendMessage())
client.add_cog(serverMcstarter(client))
client.add_cog(msgLogger(client))
client.add_cog(nonAsync(client))
client.add_cog(command(client))
client.add_cog(general(client))

try: client.run(token)
finally: save()