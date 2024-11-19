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

# Nom du salon où les messages seront envoyés
CHANNEL_NAME = "bugs-👾"
SOLVED_NAME = "bugs-✅"


@bot.event
async def on_ready():
  print(f"{bot.user} est connecté et prêt à l'emploi!")


@bot.event
async def on_raw_reaction_add(payload):

  # Vérifie si l'emoji est ✅
  if str(payload.emoji.name) == "✅":

    # Récupère le serveur (guild)
    guild = bot.get_guild(payload.guild_id)

    if guild is None:
      print("Erreur: Impossible de récupérer la guilde.")
      return

    # Récupère le salon et le message
    channel = guild.get_channel(payload.channel_id)

    if channel is None:
      print("Erreur: Impossible de récupérer le salon.")
      return

    # Vérifie que le salon est un TextChannel
    if not isinstance(channel, discord.TextChannel):
      print(f"Erreur: Le salon {channel.name} n'est pas un TextChannel.")
      return

    # Récupère le message
    try:
      message = await channel.fetch_message(payload.message_id)
    except discord.errors.NotFound:
      print("Erreur: Message introuvable.")
      return

    user = guild.get_member(payload.user_id)

    if user is None:
      print("Erreur: Impossible de récupérer l'utilisateur")
      return

    user_roles = [role.id for role in user.roles]

    # Vérifie si l'utilisateur a le rôle de dev
    dev_role = discord.utils.get(guild.roles, name=DEV_ROLE_NAME)

    if dev_role is None:
      print(f"Erreur: Le rôle '{DEV_ROLE_NAME}' n'existe pas")
      return

    if dev_role.id in user_roles and channel.name == CHANNEL_NAME:

      # Trouve le salon cible "bugs-✅"
      target_channel = discord.utils.get(guild.channels, name="bugs-✅")

      if target_channel is None:
        print("Erreur: Impossible de récupérer le salon.")
        return

      # Vérifie que le salon est un TextChannel
      if not isinstance(target_channel, discord.TextChannel):
        print(f"Erreur: Le salon {channel.name} n'est pas un TextChannel.")
        return

      try:
        # Prépare le contenu du message à envoyer
        content = (
            f"**Auteur**: {message.author.mention}\n"
            f"**Contenu**: {message.content if message.content else '*Pas de texte*'}\n"
        )

        # Prépare les fichiers joints
        files = [await attachment.to_file() for attachment in message.attachments]

        # Envoie le message texte et les fichiers dans le salon cible
        await target_channel.send(content=content, files=files)

        await message.delete()
        print(f"Message déplacé de {channel.name} vers {target_channel.name}.")
      except discord.errors.Forbidden:
        print("Erreur: Permissions insuffisantes pour supprimer le message.")
      except discord.errors.NotFound:
        print("Erreur: Le message était déjà supprimé.")


bot.run(my_secret)
