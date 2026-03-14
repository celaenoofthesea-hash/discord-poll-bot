import discord
from discord import app_commands
from discord.ext import commands

TOKEN = "MTQ4MTM1ODIyNDk5MjIzOTY1Ng.G02tqq.hJudsG3Rcm_pSdtE2usik6JJr68oHrlnHsA4qI"

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
        self.going = {}
        self.not_going = {}
        self.maybe = {}

    def make_content(self):
        msg = f"📅 **Событие назначено на: {self.date}**\n\n"
        msg += f"✅ **Приду ({len(self.going)}):**\n"
        msg += "\n".join(self.going.values()) if self.going else "—"
        msg += "\n\n"
        msg += f"❌ **Не приду ({len(self.not_going)}):**\n"
        msg += "\n".join(self.not_going.values()) if self.not_going else "—"
        msg += "\n\n"
        msg += f"❓ **Возможно ({len(self.maybe)}):**\n"
        msg += "\n".join(self.maybe.values()) if self.maybe else "—"
        return msg

    async def handle_click(self, interaction, target_dict):
        uid = interaction.user.id
        name = interaction.user.display_name
        for d in [self.going, self.not_going, self.maybe]:
            d.pop(uid, None)
        target_dict[uid] = name
        await interaction.response.edit_message(content=self.make_content(), view=self)

    @discord.ui.button(label="Приду", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, self.going)

    @discord.ui.button(label="Не приду", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, self.not_going)

    @discord.ui.button(label="Возможно", style=discord.ButtonStyle.secondary)
    async def maybe_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, self.maybe)

@bot.tree.command(name="опрос", description="Создать опрос на указанную дату")
@app_commands.describe(дата="Введите дату и время события")
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

bot.run(TOKEN)
