from discord.ext import commands
import dotenv
import os

dotenv.load_dotenv('.env')
TOKEN = os.getenv('TOKEN')
client = commands.Bot(command_prefix='$')
guild = None

async def copy_channels(guild, backup_guild, messages=True):
    for channel in backup_guild.channels:
        print(f'Deleting channel #{channel.name}...')
        await channel.delete()
        print(f'Deleted channel #{channel.name}')

    for category in guild.categories:
        print(f'Creating category {category.name}...')
        new_category = await backup_guild.create_category(
            name=category.name, position=category.position
        )
        
        for text_channel in category.text_channels:
            print(f'Creating text channel #{text_channel.name}...')
            new_text_channel = await new_category.create_text_channel(
                name=text_channel.name, 
                position=text_channel.position
            )
            
            if not messages:
                continue

            webhooks = {}
            messages = await text_channel.history(limit=None, oldest_first=True).flatten()
            count = len(messages)
            for i, message in enumerate(messages):
                webhook = webhooks.get(message.author.name)
                if not webhook:
                    webhook = await new_text_channel.create_webhook(name=message.author.name)
                    webhooks[message.author.name] = webhook

                content = message.content
                embeds = message.embeds
                files = [await a.to_file() for a in message.attachments]
                username = message.author.name
                avatar_url = message.author.avatar_url
                
                for embed in embeds:
                    if embed.type == 'gifv':
                        embeds = []

                print(f'Sending message {message.id} in #{text_channel.name}...')

                try:
                    await webhook.send(
                        content=content, 
                        embeds=embeds, 
                        files=files, 
                        username=username, 
                        avatar_url=avatar_url
                    )
                except:
                    pass

                percent = round(i / count * 100, 2)
                print(f'Sent message {message.id} in #{text_channel.name} ({i}/{count} - {percent}%)')

            print(f'Created text channel #{text_channel.name}')

        for voice_channel in category.voice_channels:
            print(f'Creating voice channel #{voice_channel.name}...')
            await new_category.create_voice_channel(
                name=voice_channel.name,
                position=voice_channel.position
            )
            print(f'Created voice channel #{voice_channel.name}')

        print(f'Created category {category.name}')

async def copy_roles(guild, backup_guild):
    for role in backup_guild.roles:
        if role.is_default() or role.is_bot_managed() or role.is_integration():
            continue

        print(f'Deleting role @{role.name}...')
        await role.delete()
        print(f'Deleted role @{role.name}')

    for role in guild.roles[::-1]:
        if role.is_default() or role.is_bot_managed() or role.is_integration():
            continue

        print(f'Creating role @{role.name}...')
        new_role = await backup_guild.create_role(
            name=role.name, 
            colour=role.color, 
            permissions=role.permissions,
            hoist=role.hoist,
            mentionable=role.mentionable,
        )

        try:
            await new_role.edit(position=role.position)
        except:
            pass

        print(f'Created role @{role.name}')

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
async def paste(context, flag=None):
    if not guild:
        await context.send('ERROR: No guild copied')
        return
    
    if flag == 'all':
        print(f'Pasting {guild.name}...')
        await copy_roles(guild, context.guild)
        await copy_channels(guild, context.guild)
        print(f'Pasted {guild.name}')
    elif flag == 'channels':
        print(f'Pasting {guild.name} channels...')
        await copy_channels(guild, context.guild, messages=False)
        print(f'Pasted {guild.name} channels')
    elif flag == 'messages':
        print(f'Pasting {guild.name} messages...')
        await copy_channels(guild, context.guild, messages=True)
        print(f'Pasted {guild.name} messages')
    elif flag == 'roles':
        await context.send(f'Pasting {guild.name} roles...')
        await copy_roles(guild, context.guild)
        await context.send(f'Pasted {guild.name} roles')
    elif flag == 'settings':
        await context.send(f'Pasting {guild.name} settings...')
        await context.send(f'Pasted {guild.name} settings')
    else:
        await context.send('ERROR: Invalid flag')  

client.run(TOKEN)
