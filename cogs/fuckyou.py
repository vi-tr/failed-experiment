import discord
from discord.ext import commands

# Здесь мы создаем класс наследующийся от commands.Cog
# __init__(ес вы плохи в ящерсокм языке) это конструктор
# он будет одинаков везде. А после делаем всё как показано тут
# отличие от варианта без cog, в случае если вы пишите всё в одном файле
# то что вы обязаны писать @commands, а не bot или как вы там назвали свой клиент
# Так как это класс, первым параметром своего метода вы должны передавать self
class Fuckyou(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @commands.command(name='lend_money')
    async def fuckyou(self, ctx):
        await ctx.send("ПОШЕЛ НАХУЙ!")    

# Вот эту хрень нужно пистаь обязательно 
# На самом деле ничего сложного тут  нет
# Вся разница в вашем случае, будет  за-
# ключаться в том, что вам вместо  лако-
# ничного Fuckyou,  нужно  будет  ввести
# название вашего класса 
async def setup(bot):
    await bot.add_cog(Fuckyou(bot))