import os,re,json,logging,discord,requests
from time import time,sleep
from random import randint
from shutil import copytree
from NHentai import NHentai
from pickle import load,dump
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

# settings
msgToConsole = True


def setupLogger(name,log_file,level=logging.WARNING):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s','%d/%m/%Y %H:%M:%S')
    fileHandler = logging.FileHandler(log_file, mode='a',encoding='utf-8')
    fileHandler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(fileHandler)
    return logger
# startup
os.chdir(r'S:\ProgrammingProjects\&DiscordBots\the mcfuck')
load_dotenv()
token=os.getenv('token')
admins = [int(i) for i in os.getenv('admins').split(',')]
moderators = [int(i) for i in os.getenv('moderators').split(',')]
hypixelKey = os.getenv('hypixelKey')
outputLog = setupLogger('output log','logs/output.log')
sentLog = setupLogger('sent log','logs/messages/sent.log')
editedLog = setupLogger('edited log','logs/messages/edited.log')
deletedLog = setupLogger('deleted log','logs/messages/deleted.log')
client = commands.Bot(command_prefix='mcfuck!')
client.remove_command('help')
logModes = {'r':'responded ','s':'status changed to ','n':''}
hentaiLanguages = {'e':'english','j':'japanese','c':'chinese'}
bannedVariables = ['token','__file__','qa','userqa','godqa','hypixelKey']
powersofTwo = [16,32,64,128,256,512,1024,2048,4096]
nhentai = NHentai()
godExempt = True
maxRoll = 16384

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
    if ctx.author.id == 234395307759108106: return
    modColors = '\033[92m' if ctx.author.id in moderators else '\033[0m'
    colorReset = '\033[0m'
    match type:
        case 's':
            log=f'{ctx.author} sent "{ctx.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
            if msgToConsole and not ctx.author.bot and '' not in ctx.content: print(f'{ctx.author} sent "{modColors}{ctx.content}{colorReset}" in {ctx.channel}{colorReset}')
            sentLog.warning(log)
        case 'd':
            log=f'"{ctx.content}" by {ctx.author} was deleted in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
            if msgToConsole and '' not in ctx.content: print(f'"{modColors}{ctx.content}{colorReset}" by {ctx.author} was deleted in {ctx.channel}{colorReset}')
            deletedLog.warning(log)
        case 'e':
            if ctx.content == ctx2.content: return
            log=f'{ctx.author} edited "{ctx.content}" into "{ctx2.content}" in {"" if ctx.guild == None else f"{ctx.guild} - "}{ctx.channel}{ext}'
            if msgToConsole and '' not in ctx.content: print(f'{ctx.author} edited "{modColors}{ctx.content}{colorReset}" into "{modColors}{ctx2.content}{colorReset}" in {ctx.channel}{colorReset}')
            editedLog.warning(log)
def messageCount(ctx):
    userID = str(ctx.author.id)
    messages.update({userID:(messages[userID])+1}) if userID in messages else messages.update({userID:1})
    saveAll()
def messageBackup():
    copytree(f'{os.getcwd()}\\logs', f'{os.getcwd()}\\backups\\logs\\{datetime.fromtimestamp(time()).strftime("%d.%m.%Y %H.%M.%S")}')
async def autoResponse(ctx):
    global godExempt
    response = ''
    if ctx.author.bot: return
    if ctx.author.id == 250797109022818305:
        if ctx.content in godqa: await ctx.channel.send(godqa[ctx.content]); logEvent(ctx,godqa[ctx.content],'r')
        if ctx.content in userqa and godExempt == False: await ctx.channel.send(userqa[ctx.content]); logEvent(ctx,userqa[ctx.content],'r')
    else:
        if ctx.content in userqa:
            for i in userqa[ctx.content]:
                if randint(0,1): response += f'​{i}​'
                else: response += i
            await ctx.channel.send(response); logEvent(ctx,response,'r')
            if foundstuffs[int(list(userqa.keys()).index(ctx.content))] == 0: foundstuffs[int(list(userqa.keys()).index(ctx.content))] = 1; await ctx.channel.send('NEW AUTO RESPONSE FOUND'); saveAll()
@client.event
async def on_ready():
    outputLog.warning(f"{client.user.name} connected to Discord!")
    print(f"{client.user.name} connected to Discord!\n")
@client.event
async def on_message(message):
    logMessages(message,'s',' - image or embed') if message.content == "" else logMessages(message,'s')
    if message.author.id == 713586207119900693: messageBackup()
    messageCount(message)
    if message.author.bot: return
    await autoResponse(message)
    await client.process_commands(message)
@client.event
async def on_message_delete(message):
    if message.author == client.user and re.sub('​','',message.content) in userqa:
        while True:
            try: await message.channel.send(message.content); break
            except: sleep(0.1)
    logMessages(message,'d',' - image or embed') if message.content == "" else logMessages(message,'d')
@client.event
async def on_message_edit(message_before,message_after):
    logMessages(message_before,'e',message_after,' - image or embed') if message_after.content == "" else logMessages(message_before,'e',message_after)
@client.command(name='leaderboard')
async def leaderboard(ctx,arg=None):
    global idNameCache,messages
    match arg:
        case '-m':
            messages = {key: value for key, value in sorted(messages.items(), key=lambda item: item[1],reverse=True)}
            response = ''
            username = ''
            index = 1
            for i in messages:
                oldResponse = response
                if i in idNameCache: username = idNameCache[i]
                else:
                    logEvent(ctx,f'adding {i} to ID cache')
                    user = await client.fetch_user(i)
                    idNameCache.update({i:user.name})
                    username = idNameCache[i]
                rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
                response += f'{rank} - {username}: {messages[i]}\n'
                if len(response)+20 > 2048: response = oldResponse; break
            await ctx.send(embed=discord.Embed(title='Message Leaderboard:',description=response,color=0x69ff69))
            logEvent(ctx,'with message leaderboard','r')
            saveAll()
        case _:
            await ctx.send('unknown leaderboard.')
@client.command(name='clearIDcache')
async def clearIDcache(ctx):
    global idNameCache
    if ctx.author.id not in admins: return
    idNameCache = {}
    logEvent(ctx,'cleared user ID cache')
    await ctx.send('done')
@client.command(name='godExempt')
async def exemptGod(ctx,arg=True): 
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
    await ctx.send(f'```{type(variable)}\n{variable}```')
@client.command(name='messageBackup')
async def messageBackupcmd(ctx):
    messageBackup()
    await ctx.send('done')
@client.command(name='roll')
async def roll(ctx,roll):
    modifiers = 0
    for i in roll.split('+'):
        if 'd' in i: roll = i
        else: modifiers += int(i)
    try: roll = roll.split('d'); roll[0] = int(roll[0]); roll[1] = int(roll[1])
    except: await ctx.send('argument error.'); return
    for i in roll:
        if i > maxRoll:
            await ctx.send(f'rolls cannot be above {(format(maxRoll,",d"))}'); return
    response = ''; total = 0
    for i in range(roll[0]): rand = randint(1,roll[1]); response += f'{rand},'; total += rand
    total += modifiers; total = (format(total,',d'))
    try: await ctx.send(embed=discord.Embed(title='rolls:',description=f'[{response[:-1]}]',color=0x69ff69).add_field(name='Modifiers:',value=modifiers).add_field(name='Total:',value=total))
    except: await ctx.send(embed=discord.Embed(title='rolls:',description='total rolls above character limit.',color=0x69ff69).add_field(name='Modifiers:',value=modifiers).add_field(name='Total:',value=total))
@client.command(name='getName')
async def getName(ctx,id):
    if len(id) != 18: await ctx.send('id error'); return
    try: user = await client.fetch_user(id)
    except: await ctx.send('id error'); return
    await ctx.send(user.name)
@client.command(name='getid')
async def getid(ctx,name):
    await ctx.send(int(re.sub('[<@!>]','',name)))
@client.command(name='getAvatar')
async def getAvatar(ctx,*idsI,res=512):
    users = ''
    ids = []
    for i in idsI:
        if i.startswith('-'):res = ''; res = int(res.join(re.findall(r'\d+',re.sub('-','',i)))); continue
        i = re.sub('[<@!>]','',i)
        ids.append(re.sub('[<@!>]','',i))
        if len(re.sub('[<@!>]','',i)) != 18: await ctx.send('id or argument error'); return
    if res not in powersofTwo: await ctx.send('size must be a power of 2 between 16 and 4096'); return
    for i in ids:
        try: user = await client.fetch_user(i)
        except: await ctx.send('id error'); return
        users += f'{user.avatar_url_as(format="png",size=res)}\n'
    await ctx.send(users[:-1])
@client.command(name='exec')
async def execCommand(ctx,*args):
    if ctx.author.id not in admins: await ctx.send('no, fuck you'); return
    command = ''
    for i in args: command += f'{i} '
    await ctx.send(eval(command[:-1]))

# I'll do this later, I'm tired.
# @client.command(name='hypixel')
# async def hypixel(ctx):
#     print(json.loads(requests.get('https://api.hypixel.net/player',params={'key':hypixelKey,'name':'test'}).text))

# help commands
@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(title='Help',description='mcfuck!help <command> for more info',color=0x69ff69)
    embed.add_field(name='user commands',value='getAvatar\ngetid\ngetName\nhentai\nleaderboard\nroll')
    embed.add_field(name='admin commands',value='clearIDcache\nexec\nget\ngodExempt\nmessageBackup')
    await ctx.send(embed=embed)
@help.command(name='getAvatar')
async def help_getAvatar(ctx): await ctx.send(embed=discord.Embed(title='getAvatar',description='get the avatar of a user. default resolution is 512.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!getAvatar <id or @ping> -[res]',inline=False).add_field(name='Example',value='mcfuck!getAvatar 821021462604677140 @the mcfuck. -256',inline=False))
@help.command(name='getid')
async def help_getid(ctx): await ctx.send(embed=discord.Embed(title='getid',description='get userid from @ping.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!getid <@ping>',inline=False).add_field(name='Example',value='mcfuck!getid @the mcfuck.',inline=False))
@help.command(name='getName')
async def help_getName(ctx): await ctx.send(embed=discord.Embed(title='getName',description='get username from id.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!getName <id>',inline=False).add_field(name='Example',value='mcfuck!getName 821021462604677140',inline=False))
@help.command(name='hentai')
async def help_hentai(ctx): await ctx.send(embed=discord.Embed(title='hentai',description='give random hentai or give sauce from id.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!hentai [id]').add_field(name='Example',value='mcfuck!hentai 177013',inline=False))
@help.command(name='leaderboard')
async def help_leaderboard(ctx): await ctx.send(embed=discord.Embed(title='leaderboard',description='lists leaderboards.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!leaderboard -<leaderboard>').add_field(name='Leaderboards',value='-m, message leaderboard',inline=False).add_field(name='Example',value='mcfuck!leaderboard -m',inline=False))
@help.command(name='roll')
async def help_roll(ctx): await ctx.send(embed=discord.Embed(title='roll',description='simple dice roller',color=0x69ff69).add_field(name='Syntax',value='mcfuck!roll <count>d<sides>+[modifiers]',inline=False).add_field(name='Example',value='mcfuck!roll 2d6+3+1',inline=False))
@help.command(name='clearIDcache')
async def help_clearIDcache(ctx): await ctx.send(embed=discord.Embed(title='clearIDcache',description='clears the cache of ID and username links.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!clearIDcache'))
@help.command(name='exec')
async def help_exec(ctx): await ctx.send(embed= discord.Embed(title='exec',description='lets me execute whatever I want through the bot.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!exec <whatever the fuck>'))
@help.command(name='get')
async def help_get(ctx): await ctx.send(embed= discord.Embed(title='get',description='prints out given variable.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!get <variable>'))
@help.command(name='godExempt')
async def help_godExempt(ctx): await ctx.send(embed= discord.Embed(title='godExempt',description='toggles or sets if bot will auto respond to god messages.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!godExempt [bool]'))
@help.command(name='messageBackup')
async def help_messageBackup(ctx): await ctx.send(embed=discord.Embed(title='messageBackup',description='forces backup of messages.',color=0x69ff69).add_field(name='Syntax',value='mcfuck!messageBackup'))

client.run(token)
