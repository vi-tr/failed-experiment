# что-то мне подсказывает, что ниже написанное - полный пиздец, но я пока ниче лучше не придумал
from bot import *

role_dict = {
    "admin": discord.Permissions.elevated(),
    "moderator": discord.Permissions.stage_moderator(),
    "member": discord.Permissions.general()
}