from datetime import datetime
from config import Config

import disnake
from disnake.ext import commands
from Tools.exceptions import CustomError


class MarryButton(disnake.ui.View):

    def __init__(self, partner: disnake.Member):
        super().__init__()
        self.partner = partner
        self.value = None
        self.config = Config()
    
    @disnake.ui.button(label="Принять", style=disnake.ButtonStyle.green)
    async def marry_button_accept(self, button, inter):
        if self.partner.id != inter.author.id:
            await inter.response.send_message("Принять должен тот, кого вы попросили!", ephemeral=True)
        else:
            await inter.response.send_message(f'{self.partner.mention} Согласен(на) быть партнёром 🎉')
            await self.config.DB.marries.insert_one({"_id": inter.author.id, "mate": self.partner.id, 'time': datetime.now()})
            self.stop()

    @disnake.ui.button(label="Отказать", style=disnake.ButtonStyle.red)
    async def marry_button_cancel(self, button, inter):
        if self.partner.id != inter.author.id:
            await inter.response.send_message("Нажать должен(на) тот, кого вы попросили!", ephemeral=True)
        else:
            await inter.response.send_message(f'{self.partner.mention} Не согласен(на) быть партнёром')
            self.stop()

class DivorceButton(disnake.ui.View):

    def __init__(self, partner: disnake.Member):
        super().__init__()
        self.partner = partner
        self.value = None
        self.config = Config()
    
    @disnake.ui.button(label="Разорвать брак", style=disnake.ButtonStyle.red)
    async def divorce_button_accept(self, button, inter):
        if self.partner.id == inter.author.id:
            await inter.response.send_message("Принять должен тот, с кем вы сватались!", ephemeral=True)
        else:
            await inter.response.send_message(f'{self.partner.mention} Согласен(на) быть партнёром 🎉')
            await self.config.DB.marries.delete_one({"_id": inter.author.id, "mate": self.partner.id, 'time': datetime.now()})
            self.stop()

class Marries(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def is_married(self, author: disnake.Member):
        if await self.bot.config.DB.marries.count_documents({'$or': [{'_id': author.id}, {'mate': author.id}]}) == 0:
            return True
        else:
            return False

    @commands.slash_command(name='marry', description="Свадьбы")
    async def marry_cmd(self, inter):
        ...

    @marry_cmd.sub_command(name="invite", description="Предложить сыграть свадьбу кому-либо")
    async def marry_invite(self, inter, member: disnake.Member):
        if await self.is_married(inter.author):
            await inter.send(
                embed=await self.bot.embeds.simple(
                    title="Свадьба, получается <3", 
                    description=f"{inter.author.mention} предлагает {member.mention} сыграть свадьбу. Ммм...)",
                    footer={"text": "Только, давайте, без беременная в 16, хорошо?", 'icon_url': inter.author.display_avatar.url}
                ), view=MarryButton(partner=member)
            )
        elif inter.author.id == member.id:
            raise CustomError("Выйти замуж за самого себя..?")
        else:
            raise CustomError(f"Эм) Вы и/или {member.mention} женаты. На что вы надеетесь?")

    @marry_cmd.sub_command(name='divorce', description="Развод с партнёром")
    async def marry_divorce(self, inter):
        if self.is_married(inter.author):
            await inter.send(
                embed=await self.bot.embeds.simple(
                    title='Вы уверены? :(', 
                    description=f"{inter.author.mention} вдруг захотел(-а) порвать брачные узы."),
                view=DivorceButton(partner=self.bot.get_user(dict(await self.bot.config.DB.marries.find_one({'mate': inter.author.id}))['_id']) if await self.bot.config.DB.marries.count_documents({"mate": inter.author.id}) != 0 else self.bot.get_user(dict(await self.bot.config.DB.marries.find_one({'_id': inter.author.id}))['mate']))
            )
        else:
            raise CustomError("Вы и так не замужем, хихи.")


def setup(bot):
    bot.add_cog(Marries(bot))
