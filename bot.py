import nextcord
from nextcord.ext import commands
import os

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!")

loaded_count = 0
total_count = 0

for filename in os.listdir('./modules'):
    if filename.endswith('.py'):
        total_count += 1
        extension = f'modules.{filename[:-3]}'
        try:
            bot.load_extension(extension)
            loaded_count += 1
        except Exception as e:
            print(f'Failed to load extension {extension}: {e}')

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} | Loaded {loaded_count}/{total_count} Modules")

bot.run("MTMwNDc3MTc1OTQwNDIyNDU1Mg.GB9cKe.LtEMB3wUDTTS-_PuzxiTFrbE6wywbCVXu_r5iM")