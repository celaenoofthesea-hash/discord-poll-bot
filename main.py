import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = os.environ.get("BOT_TOKEN")

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

class PollView(discord.ui.View):
    def __init__(self, date):
        super().__init__(timeout=None)
        self.date = date
        self.going, self.not_going = {}, {}

    def make_content(self):
        msg = f"📅 **Событие назначено на: {self.date}**\n\n"
        msg += f"✅ **Приду ({len(self.going)}):**\n" + ("\n".join(self.going.values()) if self.going else "—") + "\n\n"
        msg += f"❌ **Не приду ({len(self.not_going)}):**\n" + ("\n".join(self.not_going.values()) if self.not_going else "—")
        return msg

    async def handle_click(self, interaction, target_dict):
        await interaction.response.defer_update()
        
        uid, name = interaction.user.id, interaction.user.display_name
        for d in [self.going, self.not_going]:
            d.pop(uid, None)
        target_dict[uid] = name
        
        # Используем edit_original_response, так как мы сделали defer_update
        await interaction.edit_original_response(content=self.make_content(), view=self)

    @discord.ui.button(label="Приду", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, self.going)

    @discord.ui.button(label="Не приду", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, self.not_going)

@bot.tree.command(name="опрос", description="Создать опрос")
@app_commands.describe(дата="Дата и время")
async def slash_poll(interaction: discord.Interaction, дата: str):
    view = PollView(дата)
    await interaction.response.send_message(view.make_content(), view=view)

@bot.command()
async def опрос(ctx, *, date):
    try:
        await ctx.message.delete()
    except:
        pass
    view = PollView(date)
    await ctx.send(view.make_content(), view=view)

keep_alive()
bot.run(TOKEN)
