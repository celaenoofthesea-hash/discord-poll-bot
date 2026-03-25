import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

app = Flask('')
@app.route('/')
def home(): return "OK"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

class PollView(discord.ui.View):
    def __init__(self, date=""):
        super().__init__(timeout=None)
        self.date = date
        self.going = {}
        self.not_going = {}

    def make_content(self):
        d = self.date or "Уточняется"
        return (f"📅 **Событие: {d}**\n\n"
                f"✅ **Приду ({len(self.going)}):**\n" + 
                ("\n".join(self.going.values()) if self.going else "—") + 
                "\n\n❌ **Не приду ({len(self.not_going)}):**\n" + 
                ("\n".join(self.not_going.values()) if self.not_going else "—"))

    async def handle_click(self, interaction, target_dict, other_dict):
        await interaction.response.defer_update()
        uid, name = interaction.user.id, interaction.user.display_name
        other_dict.pop(uid, None)
        target_dict[uid] = name
        await interaction.edit_original_response(content=self.make_content(), view=self)

    @discord.ui.button(label="Приду", style=discord.ButtonStyle.success, custom_id="btn_g")
    async def confirm(self, interaction, button):
        await self.handle_click(interaction, self.going, self.not_going)

    @discord.ui.button(label="Не приду", style=discord.ButtonStyle.danger, custom_id="btn_n")
    async def decline(self, interaction, button):
        await self.handle_click(interaction, self.not_going, self.going)

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(PollView())
        await self.tree.sync()

bot = Bot()

@bot.tree.command(name="опрос")
async def slash_poll(interaction: discord.Interaction, дата: str):
    view = PollView(дата)
    await interaction.response.send_message(view.make_content(), view=view)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get("BOT_TOKEN"))
