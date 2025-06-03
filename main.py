import os
import discord
import dotenv
from discord.ext import commands

dotenv.load_dotenv()

my_secret = os.environ['FacildataBot']

# Configuration du bot
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Nom du rôle à surveiller
DEV_ROLE_NAME = "Équipe dev 👨‍💻"

# Paires de salons : source -> destination
CHANNEL_PAIRS = {
    "bugs-👾": "bugs-✅",
    "évolutions-🤖": "évolutions-✅"
}


@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt à l'emploi!")


@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.emoji.name) != "✅":
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        print("Erreur: Impossible de récupérer la guilde.")
        return

    channel = guild.get_channel(payload.channel_id)
    if channel is None or not isinstance(channel, discord.TextChannel):
        print(f"Erreur: Impossible de récupérer ou type incorrect pour le salon.")
        return

    if channel.name not in CHANNEL_PAIRS:
        # Ce salon n'est pas concerné
        return

    try:
        message = await channel.fetch_message(payload.message_id)
    except discord.errors.NotFound:
        print("Erreur: Message introuvable.")
        return

    user = guild.get_member(payload.user_id)
    if user is None:
        print("Erreur: Impossible de récupérer l'utilisateur.")
        return

    dev_role = discord.utils.get(guild.roles, name=DEV_ROLE_NAME)
    if dev_role is None:
        print(f"Erreur: Le rôle '{DEV_ROLE_NAME}' n'existe pas.")
        return

    if dev_role not in user.roles:
        print("Utilisateur sans le rôle requis.")
        return

    target_channel_name = CHANNEL_PAIRS[channel.name]
    target_channel = discord.utils.get(guild.channels, name=target_channel_name)

    if target_channel is None or not isinstance(target_channel, discord.TextChannel):
        print("Erreur: Impossible de récupérer le salon cible ou mauvais type.")
        return

    try:
        content = (
            f"**Auteur**: {message.author.mention}\n"
            f"**Contenu**: {message.content if message.content else '*Pas de texte*'}\n"
        )

        files = [await attachment.to_file() for attachment in message.attachments]

        await target_channel.send(content=content, files=files)
        await message.delete()
        print(f"Message déplacé de {channel.name} vers {target_channel.name}.")
    except discord.errors.Forbidden:
        print("Erreur: Permissions insuffisantes.")
    except discord.errors.NotFound:
        print("Erreur: Le message était déjà supprimé.")


bot.run(my_secret)