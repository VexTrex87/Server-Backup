import discord
from discord.ext import commands
import dotenv
import os

dotenv.load_dotenv('.env')
TOKEN = os.getenv('TOKEN')
client = commands.Bot(command_prefix='$')
guild = None

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

    for channel in context.guild.channels:
        print(f'Deleting #{channel.name}')
        await channel.delete()

    for category in guild.categories:
        print(f'Making category {category.name}')
        new_category = await context.guild.create_category(
            name=category.name, position=category.position
        )
        
        for text_channel in category.text_channels:
            print(f'Making text channel #{text_channel.name}')
            new_text_channel = await new_category.create_text_channel(
                name=text_channel.name, 
                position=text_channel.position
            )
            
            webhooks = {}
            async for message in text_channel.history(limit=None, oldest_first=True):
                webhook = webhooks.get(message.author.name)
                if not webhook:
                    webhook = await new_text_channel.create_webhook(name=message.author.name)
                    webhooks[message.author.name] = webhook

                try:
                    content = message.content
                    embeds = message.embeds
                    files = [await a.to_file() for a in message.attachments]
                    username = message.author.name
                    avatar_url = message.author.avatar_url
                    
                    print(f'Sending message {message.id}')
                    await webhook.send(
                        content=content, 
                        embeds=embeds, 
                        files=files, 
                        username=username, 
                        avatar_url=avatar_url
                    )
                except:
                    pass

        for voice_channel in category.voice_channels:
            print(f'Making voice channel #{text_channel.name}')
            await new_category.create_voice_channel(
                name=voice_channel.name,
                position=voice_channel.position
            )

    await context.send(f'Pasted {guild.name}')

client.run(TOKEN)
