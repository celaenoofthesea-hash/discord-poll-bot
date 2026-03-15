Готово. Я добавил метод defer() для слэш-команд, чтобы убрать ошибку «Приложение не отвечает», закрепил кнопки через custom_id и очистил код от комментариев.

Python
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import asyncio

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    port = int(os.environ.get("PORT", 10000))
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
        self.add_view(PollView(""))
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

    @discord.ui.button(label="Приду", style=discord.ButtonStyle.success, custom_id="btn_going")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer_update()
        uid, name = interaction.user.id, interaction.user.display_name
        self.not_going.pop(uid, None)
        self.going[uid] = name
        await interaction.edit_original_response(content=self.make_content(), view=self)

    @discord.ui.button(label="Не приду", style=discord.ButtonStyle.danger, custom_id="btn_not_going")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer_update()
        uid, name = interaction.user.id, interaction.user.display_name
        self.going.pop(uid, None)
        self.not_going[uid] = name
        await interaction.edit_original_response(content=self.make_content(), view=self)

@bot.tree.command(name="опрос", description="Создать опрос")
@app_commands.describe(дата="Введите дату и время события")
async def slash_poll(interaction: discord.Interaction, дата: str):
    await interaction.response.defer()
    view = PollView(дата)
    await interaction.followup.send(view.make_content(), view=view)

@bot.command()
async def опрос(ctx, *, date):
    try: await ctx.message.delete()
    except: pass
    view = PollView(date)
    await ctx.send(view.make_content(), view=view)

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
