import re
from datetime import datetime
import typing
import os

import disnake
from disnake.ext import commands
from Tools.links import fotmat_links_for_avatar, emoji_converter, emoji_formats
from Tools.decoders import Decoder
from Tools.exceptions import CustomError
import emoji as emj


class Utilities(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed = self.bot.embeds

    @commands.slash_command(
        description="Вывод аватара участника"
    )
    async def avatar(self, inter, user: disnake.User=None):
        user = user if user else inter.author
        embed = await self.embed.simple(
            title=f"Аватар {'бота' if user.bot else 'пользователя'} {user.name}",
            image=user.display_avatar.url
        )
        return await inter.send(embed=embed)

    @commands.slash_command(
        description='Перевод в/из азбуки морзе.'
    )
    async def morse(self, inter, variant: typing.Literal['to', 'from'], *, code):
        if variant == 'to':
            morse = Decoder().to_morse(code)
        elif variant == 'from':
            morse = Decoder().from_morse(code)

        embed = await self.embed.simple(
            title='Decoder/Encoder морзе.',
            description=morse
        )
        await inter.send(embed=embed)

    @commands.slash_command(
        description="Вывод информации о гильдии",
    )
    async def guild(self, inter):
        information = (
            f'Участников: **{len(inter.guild.members)}**',
            f'Эмодзи: **{len(inter.guild.emojis)}**',
            f'Ролей: **{len(inter.guild.roles)}**',
        )
        embed = await self.bot.embeds.simple(
            title=f'Информация о гильдии {inter.guild.name}',
            description="\n".join(information)
        )

        if inter.guild.banner:
            embed.set_thumbnail(inter.guild.banner.url)

        if inter.guild.icon:
            embed.set_thumbnail(inter.guild.icon)

        await inter.send(embed=embed)

    @commands.slash_command(
        description="Вывод информации о юзере"
    )
    async def user(self, inter, user: disnake.User = commands.Param(lambda inter: inter.author)):
        embed = await self.bot.embeds.simple(title=f'Информация о {"боте" if user.bot else "пользователе"} {user.name}')

        if user.banner:
            embed.set_image(url=user.banner.url)

        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"ID: {user.id}")
        
        main_information = [
            f"Зарегистрировался: **<t:{round(user.created_at.timestamp())}:R>**",
            f"Полный никнейм: **{str(user)}**",
        ]

        if user in inter.guild.members:
            user_to_member = inter.guild.get_member(user.id)
            second_information = [
                f"Зашёл(-ла) на сервер: **<t:{round(user_to_member.joined_at.timestamp())}:R> | {(datetime.utcnow() - user.created_at.replace(tzinfo=None)).days} дней**",
                f"Количество ролей: **{len(list(filter(lambda role: role, user_to_member.roles)))}**",
            ]

        embed.description = "\n".join(main_information) + "\n" + "\n".join(second_information) if user in inter.guild.members else "\n".join(main_information)

        await inter.send(embed=embed)

    @commands.slash_command(
        description="Получить эмодзик"
    )
    async def emoji(self, inter, *, emoji):
        if emoji in emj.EMOJI_ALIAS_UNICODE_ENGLISH:
            await inter.send(emoji)
        else:
            get_emoji_id = int(''.join(re.findall(r'[0-9]', emoji)))
            url = f"https://cdn.discordapp.com/emojis/{get_emoji_id}.webp?size=480&quality=lossless"
            embed = await self.bot.embeds.simple(
                title=f"Эмодзи **{emoji}**",
                image=await emoji_converter('webp', url)
            )

            await inter.send(embed=embed)

    @commands.slash_command(description="Данная команда может поднять сервер в топе на boticord'e")
    async def up(self, inter):
        data = {
            "serverID": str(inter.guild.id),
            "up": 1,
            "status": 1,
            "serverName": inter.guild.name,
            "serverAvatar": str(inter.guild.icon),
            "serverMembersAllCount": inter.guild.member_count,
            "serverMembersOnlineCount": 0,
            "serverOwnerID": str(inter.guild.owner_id),
        }

        async with self.bot.session.post(
            'https://api.boticord.top/v1/server', 
            headers={'Authorization': os.environ['BCORD']}, json=data
        ) as response:
            x = await response.json()
        
            if not response.status == 200:
                pass

            server = data["serverID"]
            embed = await self.bot.embeds.simple(
                self, 
                inter, 
                title='BotiCord', 
                description="У меня нет доступа к API методу(\nЗайдите на [сервер поддержки](https://discord.gg/43zapTjgvm) для дальнейшей помощью" if "error" in x else x["message"], 
                url=f"https://boticord.top/add/server" if "error" in x else f"https://boticord.top/server/{server}"
            )
            await inter.respond(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Utilities(bot))
