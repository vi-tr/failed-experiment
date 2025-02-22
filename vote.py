import discord
import asyncio
import time
from datetime import datetime
from typing import List, Set, Final
from logging import getLogger
from enum import Enum
from math import ceil

_logger = getLogger(__name__)

class Importance(Enum):
    minor=1; medium=2; major=3
    def timeout(self) -> int:
        match self:
            case Importance.minor: return 3600 # 1 hour
            case Importance.medium: return 259200 # 3 days
            case Importance.major: return 2629800 # 1 month
    def count(self) -> float:
        match self:
            case Importance.minor: return 0.1
            case Importance.medium: return 0.3
            case Importance.major: return 0.6

def bar_gen(percentage: float, size: int):
    chars: Final[str] = ' ▁▂▃▄▅▆▇█'
    pos = percentage*size
    return '█'*int(pos) + ('' if int(pos)==pos else chars[int(pos%1.0*len(chars))]) + ' '*(size-ceil(pos))


async def vote(client: discord.Client,
        # Equivalent to the overlap of abc.Messageable and abc.GuildChannel.
        # Don't know the proper way to do this in python yet.
        ctx: discord.TextChannel | discord.VoiceChannel | discord.StageChannel,
        title: str, options: List[str],
        symbols: str='thumbs',
        timeout: float|None=None, count: float|None=None,
        desc: str|None=None, importance: Importance=Importance.medium) -> Set[int]:

    endtime = time.time() + (importance.timeout() if timeout is None else timeout)
    count = max(1, int(len(ctx.guild.members) * (importance.count() if count is None else count))) # Floor, not round

    embed = discord.Embed(title=title,
        description=f"{desc or ''}\nГолосование будет окончено автоматически в {datetime.fromtimestamp(endtime).strftime('%Y-%m-%d %H:%M:%S')}, либо когда проголосуют {count} человек(а).",
        colour=0xed333b, timestamp=datetime.now()
    )
    embed.set_author(name="Голосование")
    symbol_set: List[str] = []
    match symbols:
        case 'thumbs':
            match len(options):
                case 2: symbol_set = ["👍", "👎"]
                case 3: symbol_set = ["👍", "✊", "👎"]
                case _: assert False
        case 'letters':
            symbol_set = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾"]
        case 'numbers':
            symbol_set = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    assert len(options) <= len(symbol_set), 'Количество опций голосование превышает количество доступных символов'

    for i, f in enumerate(options): embed.add_field(name=f, value=symbol_set[i]+" (0)", inline=False)
    msg = await ctx.send(embed=embed)
    for i in range(len(options)): await msg.add_reaction(symbol_set[i])
    _logger.info(f"Vote {msg.id} started")
    result: Set[int] = set()
    try:
        votes = [0]*len(options)
        while sum(votes) < count:
            add, remove = asyncio.create_task(client.wait_for('reaction_add')), asyncio.create_task(client.wait_for('reaction_remove'))
            first = (await asyncio.wait([add, remove], return_when=asyncio.FIRST_COMPLETED, timeout=endtime-time.time()))[0].pop()
            if first is add: remove.cancel(); votes[idx]+=1
            else:            add.cancel();    votes[idx]-=1
            for i in range(len(options)):
                embed.set_field_at(i, name=embed.fields[i].name, value=f"{symbol_set[i]} {bar_gen(votes[i]/sum(votes),20)} ({votes[i]})", inline=False)
            await msg.edit(embed=embed)
        result.add(max(enumerate(votes),key=lambda x:x[1])[0])
        _logger.info(f"Vote {msg.id} finished successfully")
    except asyncio.TimeoutError: _logger.info(f"Vote {msg.id} timed out")
    return result
