import discord
client = discord.Client()
@client.event
async def on_message(message):
    if message.author.id == 434133025450754058: await message.channel.send('justib i lov you plsb')
client.run('ODM3MTgxNzQ1NzQwNjQ0MzYy.YIo0Qg.bN13rkJxHJykczzwiO2bIdIuZWk')