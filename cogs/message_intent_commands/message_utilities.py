import sys
import platform

import disnake
import psutil
from disnake.ext import commands


class MessageUtilities(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats", description="Статистика бота")
    async def message_utilities_stats(self, ctx):
        guilds_info = (
            f"Количество серверов: **{len(self.bot.guilds)}**",
            f"Количество пользователей: **{len(self.bot.users)}**",
            f"Количество стикеров: **{len(self.bot.stickers)}**",
            f"Количество эмодзи: **{len(self.bot.emojis)}**",
        )
        about_me_info = (
            f"Я создана: **13 июля, 2021 года.**",
            f"Мой сервер поддержки: [тыкни сюда](https://discord.gg/43zapTjgvm)",
            f"Операционная система: **{platform.platform()}**",
            f"Язык программирования: **Python {sys.version}**"
        )
        other_info = (
            f"Мой ID: **{ctx.me.id}**",
            f"Количество слэш команд: **{len(self.bot.global_slash_commands)}**",
            f"Количество обычных команд: **{len([i for i in self.bot.commands if not i.name == 'jishaku'])}**",
            f"Задержка: **{round(self.bot.latency*1000, 2)}ms**",
            f"RAM: **{psutil.virtual_memory().percent}%**",
            f"CPU: **{psutil.cpu_percent()}%**"
        )
        embed = await self.bot.embeds.simple(
            title="Моя статистика и информация обо мне",
            description=f"Время, сколько я работаю - <t:{round(self.bot.uptime.timestamp())}:R> - ||спасите... ***моргнула 3 раза***||",
            url="https://leylabot.ml/",
            fields=[
                {"name": "Информация о серверах", "value": '\n'.join(guilds_info), "inline": True},
                {"name": "Информация про меня", "value": '\n'.join(about_me_info), "inline": True},
                {"name": "Всё прочее", "value": '\n'.join(other_info), "inline": True}
            ],
            footer={"text": f"Мои создатели: {', '.join([str(self.bot.get_user(i)) for i in self.bot.owner_ids])}", "icon_url": ctx.me.avatar.url}
        )

        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(MessageUtilities(bot))
