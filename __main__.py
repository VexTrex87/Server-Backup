import discord
from discord.ext import commands
import dotenv
import os

dotenv.load_dotenv('.env')
client = commands.Bot(command_prefix='$')
guild = None

def get_object(objects, value):
    for obj in objects:
        try:
            if obj.name == value or value == obj.mention or str(obj.id) in value or obj.id == int(value):
                return obj
        except:
            pass

@client.event
async def on_ready():
    print('Ready')

@client.command()
async def ping(context):
    ping = round(client.latency * 1000)
    await context.send(f'{ping} ms')

@client.command()
async def copy(context):
    global guild
    guild = context.guild
    await context.send(f'Copied {guild.name}')

@client.command()
async def paste(context):
    if not guild:
        await context.send('ERROR: No guild copied')
        return
    
    await context.send(f'Coping {guild.name}...')
    server_messages = {}
    count = 0

    for channel in guild.text_channels:
        backup_channel = get_object(context.guild.text_channels, channel.name)
        messages = await channel.history(limit=None, oldest_first=True).flatten()
        count += len(messages)
        server_messages[backup_channel] = messages

    copied_messages = 0
    rounded_percent = 0
    for channel, messages in server_messages.items():
        webhook = await channel.create_webhook(name=channel.name)
        for message in messages:
            copied_messages += 1

            embeds = message.embeds
            for embed in embeds:
                if embed.type == 'gifv':
                    embeds = []
                    break

            try:
                await webhook.send(
                    content=message.content, 
                    embeds=embeds, 
                    files=[await a.to_file() for a in message.attachments], 
                    username=message.author.name, 
                    avatar_url=message.author.avatar_url
                )
            except:
                pass

            percent = round(copied_messages / count * 100, 2)
            print(f'Sent message {message.id} in #{channel.name} ({copied_messages}/{count} - {percent}%)')
            if round(percent) != int(rounded_percent):
                rounded_percent = str(round(percent))
                await client.change_presence(activity=discord.Game(f'{rounded_percent}%'))

    await context.send(f'Copied {guild.name}')
    await client.change_presence(activity=discord.Game(f'Done!'))

client.run(os.getenv('TOKEN'))
