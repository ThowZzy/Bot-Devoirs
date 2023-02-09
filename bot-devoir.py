import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime
import requests
from icalendar import Calendar
from pytz import timezone
from sqlite3 import *
import re
import typing
intents = discord.Intents.all()
client = commands.Bot(command_prefix='$', intents=intents)

#ID des rôles qui permettent de modifier la BD
role_ids=[943537838983630878]

#Liste d'ID des personnes autorisées à modif la BD
list_users=[274654402139258885, 234673558935175168]

conn = connect("database.sqlite")

@client.event
async def on_ready():
    print("Ready.")


@client.event
async def on_command_error(ctx, error):
    await ctx.send(error)


def is_authorized(ctx):
    for role in ctx.message.author.roles:
        for role_hardcoded in roles_ids:
            if role.id==role_hardcoded: #Autorise un certain role à faire les commandes (ID)
                return true
    if ctx.message.author.id in list_users: #Autorise les utilisateurs spécifiés (leur ID)
        return True
    return False


def create_database():
	conn = connect("database.sqlite")
	cur = conn.cursor()
	cur.executescript("create table messages (id_channel int, id_embed int, id_server int, link text)")
	cur.close()
	conn.close()

#Création DB si non existante
if not os.path.isfile("database.sqlite"):
    create_database()
    print("Base de données créée.")


@commands.check(is_authorized)
@client.command(brief="Lier l'agenda à un channel avec un lien E-Learn",
                description="Lier l'agenda à un channel, ce channel aura un embed qui sera mit à jour toutes les 5 secondes")
async def agenda(ctx, channel: discord.TextChannel, link):
    if not valid_link(link):
        await ctx.send("Lien invalide !\nExemple de lien : https://learn-technique.helmo.be/calendar/export_execute.php?userid=ID&authtoken=TOKEN&preset_what=all&preset_time=recentupcoming")
        return
        
    guild_id = ctx.message.guild.id
                
    embed = discord.Embed(title="Devoirs (Moodle)", color=0x00ff00,
                                              timestamp=datetime.datetime.now().astimezone(timezone('Europe/Brussels')))
    embed.set_footer(text="Récupération des devoirs..")
    embed_id = await channel.send(embed=embed, components=[
    discord.Button(style=discord.ButtonStyle.green, label="Description des devoirs")])
    cur = conn.cursor()
    cur.execute(f"insert into messages (id_channel, id_embed ,id_server, link) values (?, ?, ?, ?)", (channel.id, embed_id.id, guild_id, link))
    conn.commit()
    cur.close()
    await ctx.send(f"Agenda assigné à {channel.mention}")


@commands.check(is_authorized)
@client.command(name="bd",
                brief="Supprimer un embed de la base de donné ou afficher la DB", 
                description=f"Supprimer un embed de la base de donné ou afficher la DB. Usage: {client.command_prefix}bd <del|show> <ID|Optionnal>")
async def bd(ctx, command, ID=None):
    guild_id = ctx.message.guild.id
    if command == 'del':
        if ID is None:
            await ctx.send(f"ID de l'embed manquant.\nEX: {client.command_prefix}bd del 941048683221377054")
        else:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM messages WHERE id_embed = ?;", (ID,))
            conn.commit()
            cur.close()
            await ctx.send(f"Embed {ID} supprimé (Si existant)")
    elif command == 'show':
        embed_edit=discord.Embed(title="Contenu base de données", description="Recupération des données de la BD et vérification de l'existence de chaque embed...")
        embed_edit=await ctx.send(embed=embed_edit)
        cur = conn.cursor()
        cur.execute(f"select * from messages where id_server = ?", (guild_id,))
        values=cur.fetchall()
        cur.close()
        empty=True
        k=1
        description=""
        for value in values:
            empty=False
            if value[1]:
                erreur=False
                message=None
                channel=None
                try:
                    channel = client.get_channel(value[0])
                    message=await channel.fetch_message(int(value[1]))
                except:
                    erreur=True
                if not erreur:
                    description+=f"[{k}] Embed [{message.id}]({message.jump_url}) avec comme lien [LIEN]({value[3]}) dans {channel.mention}"
                else:
                    description+=f"[{k}] Embed {value[1]} avec comme lien : [LIEN]({value[3]})"
                    if not channel:
                        description+=f"\n[{k}] ⚠️ Channel introuvable !"
                    else:
                        description+=f"\n[{k}] ⚠️ Message introuvable ! (Dans {channel.mention})"
                description+="\n\n"
                k+=1
        if empty:
            embed = discord.Embed(title="Contenu base de données", description="La BD liée à ce serveur est vide.")
            await embed_edit.edit(embed=embed)
        else:
            embed = discord.Embed(title="Contenu base de données", description=description)
            await embed_edit.edit(embed=embed)
    else:
        await ctx.send(f"Usage: {client.command_prefix}bd <del|show> <ID|Optionnal>")


def valid_link(link):
    if not re.match("^https:\/\/learn-technique\.helmo\.be\/calendar\/export_execute\.php\?userid=",link):
        return False
    try:
        get_devoirs(link)
    except:
        return False
        
    return True



def get_devoirs(calendar):

    r = requests.get(calendar)
    gcal = Calendar.from_ical(r.text)

    devoirs = []
    doublons={}
    for event in gcal.walk('VEVENT'):
        # Get 'start' date
        if 'DTSTART' in event:
            try:
                dtstart = event['DTSTART'].dt.astimezone(timezone('Europe/Brussels'))
            except:
                dtstart = False
        # Get 'stop' date
        if 'DTEND' in event:
            try:
                dtend = event['DTEND'].dt.astimezone(timezone('Europe/Brussels'))
            except:
                dtend = False
        if event["summary"].endswith("s'ouvre"):
            continue

        now = datetime.datetime.now().astimezone(timezone('Europe/Brussels'))
        if now > dtend:
            continue
        if "CATEGORIES" in event.keys():
            if event["categories"].cats[0] not in doublons.keys():
                doublons[event["categories"].cats[0]]=0
            else:
                doublons[event["categories"].cats[0]]+=1
                if doublons[event["categories"].cats[0]]>10:
                    continue
            devoirs.append((event["summary"], event["description"], event["categories"].cats[0], dtstart, dtend))
        else:
            devoirs.append((event["summary"], event["description"], "Sans cours", dtstart, dtend))

    return devoirs


async def agenda_embed():
    while True:
        await asyncio.sleep(15)
        cur = conn.cursor()
        cur.execute("select * from messages")
        rs=cur.fetchall()
        cur.close()
        for r in rs:
            if r[0]:
                try:  # Continue l'execution en cas d'erreur innatendue
                    guild_id = r[2]
                    channel_id = r[0]
                    channel = client.get_channel(channel_id)
                    if r[1]:
                        embed_id = r[1]
                        embed_message = await channel.fetch_message(int(embed_id))
                        embed = discord.Embed(title="Devoirs (Moodle)", color=0x00ff00,
                                              timestamp=datetime.datetime.now().astimezone(timezone('Europe/Brussels')))
                        embed.set_footer(text="Mis à jour")

                        devoirs = get_devoirs(r[3])
                        for devoir in devoirs:
                            now = datetime.datetime.now().astimezone(timezone('Europe/Brussels'))
                            delta = devoir[4] - now
                            jour, heure, minutes, seconds = delta.days, delta.seconds // 3600, (
                                        delta.seconds // 60) % 60, delta.seconds % 60
                            embed_dict = embed.to_dict()
                            exists = False
                            if "fields" in embed_dict.keys():
                                for field in embed_dict["fields"]:
                                    if field["name"] == f"{devoir[2]}":
                                        field_suite_edit=None
                                        for field_suite in embed_dict["fields"]:
                                            if field_suite["name"] == f"{devoir[2]} (suite)":
                                                field_suite_edit=field_suite
                                        if field_suite_edit is not None:
                                            field_edit=field_suite_edit
                                        else:
                                            field_edit=field
                                        str=""
                                        for value in field_edit["value"]:
                                            str+=value
                                        if len(str)>1024:
                                            embed = discord.Embed.from_dict(embed_dict)
                                            embed.add_field(name=f"{devoir[2]} (suite)",
                                                    value=f"{devoir[0]} (Se ferme dans {abs(jour)}j {abs(heure)}h {abs(minutes)}m {abs(seconds)}s)",
                                                    inline=False)
                                            embed_dict = embed.to_dict()
                                            exists = True
                                            break
                                        exists = True
                                        field_edit["value"] += f"\n{devoir[0]} (Se ferme dans {abs(jour)}j {abs(heure)}h {abs(minutes)}m {abs(seconds)}s)"
                            embed = discord.Embed.from_dict(embed_dict)
                            if not exists:
                                    embed.add_field(name=f"{devoir[2]}",
                                                    value=f"{devoir[0]} (Se ferme dans {abs(jour)}j {abs(heure)}h {abs(minutes)}m {abs(seconds)}s)",
                                                    inline=False)
                        if not embed.fields:
                            embed.add_field(name="Pas de devoirs.. Profites-en pour revoir tes cours",
                                                value="\u200b")
                        await embed_message.edit(embed=embed)

                    else:
                        pass
                except Exception as error:
                    print(error)
                    # cur.execute(f"DELETE FROM messages WHERE id_embed = {embed_id} ;")
                    # conn.commit()
                    continue


async def react_button():
    while True:
        #res = await client.wait_for("button_click")
        res = await client.wait_for('interaction', check=lambda interaction: interaction.data["component_type"] == 2)
        calendar = ""
        cur = conn.cursor()
        cur.execute(f"select * from messages where id_embed = {res.message.id}")
        rs=cur.fetchall()
        cur.close()
        for r in rs:
            calendar = r[3]
        description = ""
        if calendar:
            devoirs = get_devoirs(calendar)
            for devoir in devoirs:
                if devoir[1]:
                    description += f"**{devoir[0]}:**\n{devoir[1].strip()}\n\n"
                else:
                    description += f"**{devoir[0]}:**\nPas de description disponible.\n\n"
            if description:
                embed = discord.Embed(title="Descriptions des devoirs", description=description)
            else:
                embed = discord.Embed(title="Baah il n'y a pas de devoirs")
        else:
            embed = discord.Embed(title="Ce calendrier n'est pas répertorié en BD. omg")
        await res.response.send_message(
            ephemeral=True,
            embed=embed
        )

async def main():
    async with client:
        client.loop.create_task(agenda_embed())
        client.loop.create_task(react_button())
        await client.start('TOKEN')

asyncio.run(main())
