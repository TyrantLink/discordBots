import os,re,logging,discord,asyncio
from random import randint
from pickle import load,dump
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands
from time import sleep

client = commands.Bot(command_prefix='sticc!')
client.remove_command('help')
os.chdir(r"S:\ProgrammingProjects\&DiscordBots\the discipline sticc")
logging.basicConfig(format='[%(asctime)s.%(msecs)03d] %(message)s',filename='output.log',level=logging.WARNING,datefmt='%d/%m/%Y %H:%M:%S')
load_dotenv()
token=os.getenv('token')
logModes = {'r':'responded ','s':'status changed to ','n':''}
bannedUsers = [343972120067309568]
admins = [344912616629469184,434133025450754058,250797109022818305]
bannedVariables = ['token','__file__']
days = {'🇲':0,'🇹':1,'🇼':2,'🅰':3,'🇫':4,'🇸':5,'🅱':6}
try:
    with open('save.dat','rb') as save:
        activeMemberIDs = load(save)
        currentStik = load(save)
        sticcs = load(save)
        idNameCache = load(save)
except:
    activeMemberIDs = []
    currentStik = 0
    sticcs = {}
    idNameCache = {}
try:
    with open('staticSave.dat','rb') as save:
        setupComplete = load(save)
        tsRole = load(save)
        tsChannel = load(save)
        updateDays = load(save)
except:
    setupComplete = False
    tsRole = ''
    tsChannel = ''
    updateDays = ''
activeMemberIDs = [645069774438531089, 360564186520223754, 434133025450754058, 447929529449709568, 344912616629469184, 250797109022818305, 406238128408494090, 720083946943283241, 505828770112995328, 364237299275399168, 816512113517527121, 798310578606047263]
sticcs = {}
def save(type):
    match type:
        case 'v':
            with open('save.dat','wb') as save:
                dump(activeMemberIDs,save)
                dump(currentStik,save)
                dump(sticcs,save)
                dump(idNameCache,save)
        case 's':
            with open('staticSave.dat','wb') as save:
                dump(setupComplete,save)
                dump(tsRole,save)
                dump(tsChannel,save)
                dump(updateDays,save)
def logEvent(text,ctx=None,custom=False,mode='n'):
    try: m=logModes[mode]
    except: m='unknown log mode'
    log=f"{m}{text} in {ctx.guild} - {ctx.channel}" if custom == False else f'{text}'
    logging.warning(log)
    print(log)
async def updateStatus():
    user = await client.fetch_user(currentStik)
    await client.change_presence(activity=discord.Game(f'{user.name} has the talking stick'))
async def rollTalkingStick():
    global activeMemberIDs,activeMemberNames,currentStik,sticcs
    rand = activeMemberIDs[randint(0,len(activeMemberIDs)-1)]
    while rand == currentStik: rand = activeMemberIDs[randint(0,len(activeMemberIDs)-1)]
    newStik = await server.fetch_member(rand)
    oldStik = await server.fetch_member(currentStik)
    await oldStik.remove_roles(tsRole)
    await newStik.add_roles(tsRole)
    await client.get_channel(tsChannel).send(f'congrats <@!{rand}>, you have the talking stick.')
    currentStik = rand
    sticcs.update({currentStik:(sticcs[currentStik])+1}) if currentStik in sticcs else sticcs.update({currentStik:1})
    activeMemberIDs = []
    save('v')
    logEvent(f'rerolled talking stick to {newStik}',custom=True)
async def sticcLoop():
    while datetime.now().strftime("%S") != '01': sleep(0.5); continue
    while client.is_ready:
        await asyncio.sleep(60)
        if datetime.now().strftime("%H:%M") == '09:00':
            await rollTalkingStick()
            await updateStatus()
@client.event
async def on_ready():
    global server
    log=f"{client.user.name} connected to Discord!"
    logging.warning(log)
    print(f'{log}\n')
    await updateStatus()
    server = await client.fetch_guild(559830737889787924)
@client.event
async def on_message(message):
    if message.author.id not in activeMemberIDs and message.author.id not in bannedUsers: logEvent(f'adding {message.author.name} to active members',ctx=message,custom=True); activeMemberIDs.append(message.author.id); save('v')
    await client.process_commands(message)
@client.command(name='setup')
async def setup(ctx):
    global tsRole,tsChannel,updateDays
    await ctx.send(embed=discord.Embed(title='Talking Stick Role:',description='simply ping the role',color=0x69ff69))
    activeUser = ctx.author.id
    while True:
        msg = await client.wait_for('message')
        if activeUser != msg.author.id: continue
        if re.match('<@&[0-9]{18}>',msg.content): tsRole = discord.Object(str(re.sub('[<@&>]','',msg.content))); break
        elif msg.content == 'break': await ctx.send('okay'); return
        else: await ctx.send('invalid response, just ping the role.')
    await ctx.send(embed=discord.Embed(title='Talking Stick Channel:',description='simply ping the channel',color=0x69ff69))
    while True:
        msg = await client.wait_for('message')
        if activeUser != msg.author.id: continue
        if re.match('<#[0-9]{18}>',msg.content): tsChannel = discord.Object(str(re.sub('[<#>]','',msg.content))); break
        elif msg.content == 'break': await ctx.send('okay'); return
        else: await ctx.send('invalid response, just ping the channel.')
    updateDays = []
    msg = await ctx.send(embed=discord.Embed(title='Days to reroll:',description='🇲: Monday\n🇹: Tuesday\n🇼: Wednesday\n🅰: Thursday\n🇫: Friday\n🇸: Saturday\n🅱️: Sunday\n✅: done',color=0x69ff69))
    for i in days: await msg.add_reaction(i)
    await msg.add_reaction('✅')
    sleep(.5)
    def check(reaction,user):
        if activeUser != user.id: return False
        match reaction.emoji:
            case '🇲':
                if '🇲' not in updateDays: updateDays.append(days['🇲']); return False
            case '🇹':
                if '🇹' not in updateDays: updateDays.append(days['🇹']); return False
            case '🇼':
                if '🇼' not in updateDays: updateDays.append(days['🇼']); return False
            case '🅰':
                if '🅰' not in updateDays: updateDays.append(days['🅰']); return False
            case '🇫':
                if '🇫' not in updateDays: updateDays.append(days['🇫']); return False
            case '🇸':
                if '🇸' not in updateDays: updateDays.append(days['🇸']); return False
            case '🅱':
                if '🅱' not in updateDays: updateDays.append(days['🅱']); return False
            case "✅": return True
            case _: return False
    await client.wait_for('reaction_add',check=check)
    await ctx.send(embed=discord.Embed(title='Setup Complete.',description=f'role: <@&{tsRole.id}>\n\nchannel: <#{tsChannel.id}>\n\nupdateDays: {updateDays}',color=0x69ff69))
    save('s')
@client.command(name='info')
async def setupInfo(ctx):
    await ctx.send(embed=discord.Embed(title='Bot Info:',description=f'role: <@&{tsRole.id}>\n\nchannel: <#{tsChannel.id}>\n\nupdateDays: {updateDays}',color=0x69ff69))
@client.command(name='reroll')
async def forceReroll(ctx,arg):
    if arg != '-f': return
    if ctx.author.id in admins: await rollTalkingStick(ctx); await updateStatus(); logEvent('force rerolling talking stick',ctx=ctx)
    else: logEvent('failed talking stick reroll: user not an admin',ctx=ctx)
@client.command(name='listActive')
async def listActive(ctx):
    active = ''
    for i in activeMemberIDs:
        if i in idNameCache: username = idNameCache[i]
        else:
            logEvent(f'adding {i} to ID cache',ctx=ctx)
            user = await client.fetch_user(i)
            idNameCache.update({i:user.name})
            username = idNameCache[i]
        active += f'{username}\n'
    await ctx.send(embed=discord.Embed(title='Active Users',description=active,color=0x69ff69))
@client.command(name='removeActive')
async def removeActive(ctx,id):
    if ctx.author.id not in admins: return
    if id == '*': activeMemberIDs = []; await ctx.send('done'); return
    if len(id) != 18: await ctx.send('id error'); return
    for i in range(len(activeMemberIDs)):
        if id == activeMemberIDs[i]: activeMemberIDs.pop(i); await ctx.send('done'); return
    else: await ctx.send('user was not in active list')
@client.command(name='addActive')
async def addActive(ctx,id):
    if ctx.author.id not in admins: return
    if len(id) != 18: await ctx.send('id error'); return
    if int(id) in activeMemberIDs: await ctx.send('user is already active'); return
    activeMemberIDs.append(id)
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
            logEvent(f'adding {i} to ID cache',ctx=ctx)
            user = await client.fetch_user(i)
            idNameCache.update({i:user.name})
            username = idNameCache[i]
        rank = str(index)+("th" if 4<=index%100<=20 else {1:"st",2:"nd",3:"rd"}.get(index%10, "th")); index += 1
        response += f'{rank} - {username}: {sticcs[i]}\n'
    await ctx.send(embed=discord.Embed(title='sticc Leaderboard:',description=response,color=0x69ff69))
    logEvent('with sticc leaderboard',ctx=ctx,mode='r')
    save('v')
@client.command(name='clearIDcache')
async def clearIDcache(ctx):
    global idNameCache
    if ctx.author.id not in admins: return
    idNameCache = {}
    logEvent('cleared user ID cache',ctx=ctx)
    await ctx.send('done')
@client.command(name='get')
async def get(ctx,variable=''):
    if variable=='': await ctx.send('unspecified variable.'); return
    if variable in bannedVariables: await ctx.send('no, fuck you.'); return
    if ctx.author.id not in admins: return
    try: variable = globals()[variable]
    except: await ctx.send('unknown variable name.'); return
    await ctx.send(f'```{variable}```')
@client.command(name='role')
async def role(ctx,action='',id=''):
    if action == '' or id == '': await ctx.send('argument error.'); return
    if ctx.author.id not in admins: return
    if len(id) != 18: await ctx.send('id error'); return
    match action:
        case 'remove': 
            user = await ctx.guild.fetch_member(id)
            await user.remove_roles(tsRole)
            await ctx.send('done.')
        case 'give':
            user = await ctx.guild.fetch_member(id)
            await user.add_roles(tsRole)
            await ctx.send('done.')
#help commands
@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(title='Help',description='sticc!help <command> for more info',color=0x69ff69)
    embed.add_field(name='user commands',value='listActive\nrerollDays\nsticcLeaderboard')
    embed.add_field(name='admin commands',value='addActive\nclearIDcache\nfReroll\nremoveActive\nsetDays')
    await ctx.send(embed=embed)
@help.command(name='listActive')
async def help_listActive(ctx): await ctx.send(embed=discord.Embed(title='listActive',description='lists all users who are active enough to be rolled the talking sticc.',color=0x69ff69).add_field(name='Syntax',value='sticc!listActive'))
@help.command(name='rerollDays')
async def help_rerollDays(ctx): await ctx.send(embed=discord.Embed(title='rerollDays',description='lists the days when the talking sticc will be rerolled.',color=0x69ff69).add_field(name='Syntax',value='sticc!rerollDays'))
@help.command(name='addActive')
async def help_addActive(ctx): await ctx.send(embed=discord.Embed(title='addActive',description='manually adds a user to the list of active users.',color=0x69ff69).add_field(name='Syntax',value='sticc!addActive <userID>'))
@help.command(name='fReroll')
async def help_fReroll(ctx): await ctx.send(embed=discord.Embed(title='fReroll',description='force rerolls the talking sticc, ignoring time and date.',color=0x69ff69).add_field(name='Syntax',value='sticc!fReroll'))
@help.command(name='removeActive')
async def help_removeActive(ctx): await ctx.send(embed=discord.Embed(title='removeActive',description='manually removes a user from the list of active users.',color=0x69ff69).add_field(name='Syntax',value='sticc!removeActive <userID>'))
@help.command(name='setDays')
async def help_setDays(ctx): await ctx.send(embed=discord.Embed(title='setDays',description='sets which days the talking sticc will reroll.',color=0x69ff69).add_field(name='Syntax',value='sticc!setDays <everyday/none/day1, day2, day3 etc.>'))
@help.command(name='leaderboard')
async def help_leaderboard(ctx): await ctx.send(embed=discord.Embed(title='leaderboard',description='lists leaderboard for total number of times a user has recieved the talking sticc.',color=0x69ff69).add_field(name='Syntax',value='sticc!leaderboard'))
@help.command(name='clearIDcache')
async def help_clearIDcache(ctx): await ctx.send(embed=discord.Embed(title='clearIDcache',description='clears the cache of ID and username links.',color=0x69ff69).add_field(name='Syntax',value='sticc!clearIDcache'))
client.loop.create_task(sticcLoop())
client.run(token)