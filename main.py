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

# Бот берет токен из переменной окружения Render
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
        self.going, self.not_going, self.maybe = {}, {}, {}

    def make_content(self):
        msg = f"📅 **Событие назначено на: {self.date}**\n\n"
        msg += f"✅ **Приду ({len(self.going)}):**\n" + ("\n".join(self.going.values()) if self.going else "—") + "\n\n"
        msg += f"❌ **Не приду ({len(self.not_going)}):**\n" + ("\n".join(self.not_going.values()) if self.not_going else "—") + "\n\n"
        msg += f"❓ **Кто я? Где я? Что я? ({len(self.maybe)}):**\n" + ("\n".join(self.maybe.values()) if self.maybe else "—")
        return msg

    async def handle_click(self, interaction, target_dict):
        uid, name = interaction.user.id, interaction.user.display_name
        for d in [self.going, self.not_going, self.maybe]: d.pop(uid, None)
        target_dict[uid] = name
        await interaction.response.edit_message(content=self.make_content(), view=self)

    @discord.ui.button(label="Приду", style=discord.ButtonStyle.success)
    async def confirm(self, interaction, button): await self.handle_click(interaction, self.going)

    @discord.ui.button(label="Не приду", style=discord.ButtonStyle.danger)
    async def decline(self, interaction, button): await self.handle_click(interaction, self.not_going)

    @discord.ui.button(label="Возможно", style=discord.ButtonStyle.secondary)
    async def maybe_btn(self, interaction, button): await self.handle_click(interaction, self.maybe)

@bot.tree.command(name="опрос", description="Создать опрос")
@app_commands.describe(дата="Дата и время")
async def slash_poll(interaction: discord.Interaction, дата: str):
    await interaction.response.send_message(PollView(дата).make_content(), view=PollView(дата))

@bot.command()
async def опрос(ctx, *, date):
    try: await ctx.message.delete()
    except: pass
    await ctx.send(PollView(date).make_content(), view=PollView(date))

keep_alive()
bot.run(TOKEN)
