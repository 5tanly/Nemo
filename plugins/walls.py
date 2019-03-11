#!/usr/local/bin/python3.7

#Imports
import discord
import asyncio
import sqlite3
import os
import json
import datetime
import math

import traceback

#From Imports
from discord.ext import commands
from aiohttp import ClientSession
from random import randint

#Custom Imports
import scripts.error

def execute_database(execute):
    conn = sqlite3.connect(f'{os.getcwd()}/plugins/walls/database.db')
    c = conn.cursor()
    c.execute(execute)
    conn.commit()
    fetch = c.fetchall()
    conn.close()
    return fetch

try:
    enable = execute_database("SELECT enabled FROM config")
    for row in enable:
        enabled = bool(row[0])
except:
    enabled = 3

# <<--- Initialization on loadup --->> #
def initialize():
    try:
        #Create walls directory for database and config
        os.mkdir(f'{os.getcwd()}/plugins/walls')
        #Create walls count table in database
        execute_database("CREATE TABLE walls ('discord_id' integer, 'minecraft_id' text, 'minecraft_name' text, 'checks' integer)")
        #Create configuration table in database
        execute_database("CREATE TABLE config ('start' text, 'interval' text, 'channel_id' integer, 'enabled' boolean)")
        execute_database("INSERT INTO config VALUES ('10', '5', '0', '0')")
        #Create stars table in database
        execute_database("CREATE TABLE stars ('count' integer,'star' text)")
        stars =	{":star:":50,":star2:":100,":dizzy:":150,":sparkles:":200,":comet:":250,":boom:":300,":trident:":400,":trophy:":500,":crown:":600}
        for i in stars:
                execute_database(f"INSERT INTO stars VALUES ('{stars[i]}', '{i}')")
    except:
        #Do nothing, if database exists already
        pass

# <<--- Get config variables on loadup --->> #
def config():
    cfg = execute_database("SELECT * FROM config")
    for row in cfg:
        start = row[0]
        interval = row[1]
        channel = row[2]
        enabled = row[3]
    return int(start), int(interval), int(channel), bool(enabled)

# <<--- Plugin running code below --->> #
class Walls:
    def __init__(self, bot):
        initialize()
        self.bot = bot
        self.start, self.interval, self.channel, self.enabled = config()
        channel = discord.utils.get(bot.get_guild(bot.guild_id).text_channels, name='walls')
        self.channel = channel.id

        self.weewoos = False
        self.count = 280
        self.remind = 0
        self.message = 0

        if self.enabled:
            self.task = bot.loop.create_task(self.walls_loop())

    def __unload(self):
        self.weewoo_clock = False
        try:
            self.task.cancel()
        except:
            pass

    async def walls_loop(self):
        print(self.start, self.interval)
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(self.channel)
        while True:
            print(self.count)
            if (self.count == self.start*60):
                print(f'start {self.count/60} minutes')
                pass
            elif ((self.count - self.start*60) % (self.interval*60) == 0):
                print(f'interval {self.count/60} minutes')
            await asyncio.sleep(1)
            self.count += 1

    async def on_raw_reaction_add(self, payload):
        try:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.get_message(payload.message_id)
            if payload.channel_id == self.channel and payload.emoji.name in ['✅'] and payload.user_id != self.bot.user.id:
                #If user is reacting to the correct message, emoji is ✅, and user reacting is not the bot itself
                await walls_checked(self, payload.user_id)
                await message.clear_reactions()
            elif payload.channel_id == self.channel and payload.emoji.name in ['💣'] and payload.user_id != self.bot.user.id:
                #If user is reacting to the correct message, emoji is 💣, and user reacting is not the bot itself
                await send_weewoo(self, payload.user_id)
                await message.clear_reactions()
            elif payload.channel_id == self.channel and payload.emoji.name in ['👑'] and payload.user_id != self.bot.user.id:
                #If user is reacting to the correct message, emoji is 👑, and user reacting is not the bot itself
                await send_top(self, 1)
                await message.remove_reaction('👑', self.bot.get_guild(payload.guild_id).get_member(payload.user_id))
        except:
            traceback.print_exc()
            pass

    async def on_message(self, message):
        #Disable talking in #walls channel
        channel = self.bot.get_channel(self.channel)
        if message.author.id != self.bot.user.id:
            if message.channel.id == self.channel:
                if message.content in ['!'] or not message.content.startswith('!'):
                    if message.author.id != message.guild.owner.id:
                        await message.delete()
                        await channel.send(embed=create_small_embed('shhh! no talking in here...', '', discord.Color.orange()), delete_after=3)

    @commands.group(pass_context=True, invoke_without_command=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.has_any_role('leader', 'developer')
    async def walls(self, ctx):
        await ctx.send(embed=scripts.error.embed('Invalid Option', 'Please use ``on`` or ``off``'), delete_after=10)

    @walls.command(name='on')
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.has_any_role('leader', 'developer')
    async def walls_on(self, ctx):
        await ctx.message.delete()
        if not self.enabled:
            channel = self.bot.get_channel(self.channel)
            time = f'{datetime.datetime.now().strftime("%a %b %d %I:%M %p")} EST'
            execute_database("UPDATE config SET enabled=1 WHERE enabled=0")
            await channel.send(embed=create_small_embed(f'{ctx.message.author.mention} enabled walls', time, discord.Color.gold()))
            self.bot.unload_extension('plugins.walls')
            self.bot.load_extension('plugins.walls')
        else:
            await ctx.send(embed=create_small_embed('Walls already enabled', '', discord.Color.dark_red()), delete_after=10)

    @walls.command(name='off')
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.has_any_role('leader', 'developer')
    async def walls_off(self, ctx):
        await ctx.message.delete()
        if self.enabled:
            channel = self.bot.get_channel(self.channel)
            time = f'{datetime.datetime.now().strftime("%a %b %d %I:%M %p")} EST'
            execute_database("UPDATE config SET enabled=0 WHERE enabled=1")
            await channel.send(embed=create_small_embed(f'{ctx.message.author.mention} disabled walls', time, discord.Color.gold()))
            self.bot.unload_extension('plugins.walls')
            self.bot.load_extension('plugins.walls')
        else:
            await ctx.send(embed=create_small_embed('Walls already disabled', '', discord.Color.dark_red()), delete_after=10)

    @commands.command(name='check', aliases = ['c', 'safe', 's'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_any_role('access_walls')
    async def check(self, ctx):
        await ctx.message.delete()
        await walls_checked(self, ctx.message.author.id)

    @commands.command(name='stars', aliases = ['star'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_any_role('access_walls')
    async def stars(self, ctx):
        await ctx.message.delete()
        stars = execute_database("SELECT * FROM stars ORDER BY count ASC")
        list = ''
        for row in stars:
            count = row[0]
            star = row[1]
            list += f'{star} {count}\n\n'
        await ctx.send(embed=create_medium_embed('Starboard', list, '', discord.Color.dark_gold()), delete_after=20)

    @commands.command(name='ign')
    @commands.cooldown(1, 1, commands.BucketType.guild)
    @commands.has_any_role('access_walls')
    async def ign(self, ctx, name):
        await ctx.message.delete()
        await ctx.trigger_typing()
        minecraft_id, minecraft_name = await download_user(name)
        if minecraft_id and minecraft_name:
            add_user_to_database(ctx.message.author.id, minecraft_id, minecraft_name)
            minecraft_skin = f'https://visage.surgeplay.com/face/128/{minecraft_id}?{randint(0, 2304)}'
            await ctx.send(embed=create_embed('Name updated!', 'Name:', minecraft_name, 'ID:', minecraft_id, '', minecraft_skin, discord.Color.blue(), False), delete_after=5)
        else:
            await ctx.send(embed=scripts.error.embed('Name unavailible', 'Name does not exist as a Minecraft Username on mojang.com'), delete_after=10)

    @commands.command(name='weewoo', aliases = ['w'])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.has_any_role('access_walls')
    async def weewoo(self, ctx):
        await ctx.message.delete()
        await send_weewoo(self, ctx.message.author.id)

    @commands.command(name='top', aliases = ['t'])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.has_any_role('access_walls')
    async def top(self, ctx, page_num=1):
        await ctx.message.delete()
        await send_top(self, page_num)

    @commands.command(name='alltop')
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.is_owner()
    async def alltop(self, ctx, page_num=0):
        await ctx.message.delete()
        if page_num == 0:
            await ctx.send(embed=scripts.error.embed('Page number required', 'Please enter a page number'), delete_after=10)
        else:
            for x in range(1,page_num+1):
                await send_top(self, x, delete = False)
                await asyncio.sleep(1)

# <<--- Functions --->> #
async def walls_checked(self, discord_id):
    channel = self.bot.get_channel(self.channel)
    await channel.trigger_typing()
    self.weewoo_clock = False
    if not check_if_user_in_database(discord_id):
        #User is not in database
        await channel.send(embed=scripts.error.embed('Not Registered', 'Please type !ign <name> to register'), delete_after=10)
        return False
    else:
        #User is in database
        try:
            await self.message.clear_reactions()
        except:
            pass
        try:
            await self.remind.delete()
        except:
            pass
        add_check_to_user(discord_id)
        minecraft_id, minecraft_name, checks = get_user_from_database(discord_id)
        minecraft_skin = f'https://visage.surgeplay.com/face/128/{minecraft_id}?{randint(0, 2304)}'
        star = get_star(checks, discord_id)
        if (math.floor(self.count/60) == 0):
            self.message = await channel.send(embed=create_embed('Walls Checked!', 'Name:', f'``{minecraft_name}``', 'Checks:', f'``{checks}`` {star}', f'{math.floor(self.count%60)} seconds', minecraft_skin, discord.Color.dark_green(), True))
        else:
            self.message = await channel.send(embed=create_embed('Walls Checked!', 'Name:', f'``{minecraft_name}``', 'Checks:', f'``{checks}`` {star}', f'{math.floor(self.count/60)}m {math.floor(self.count%60)}s', minecraft_skin, discord.Color.dark_green(), True))
        self.count = 0
        await self.message.add_reaction('✅')
        await self.message.add_reaction('💣')
        await self.message.add_reaction('👑')
        return True

async def send_weewoo(self, user):
    channel = self.bot.get_channel(self.channel)
    await channel.trigger_typing()
    if not check_if_user_in_database(user):
        #User is not in database
        await channel.send(embed=scripts.error.embed('Not Registered', 'Please type !ign <name> to register'), delete_after=10)
        return False
    else:
        #User is in database
        try:
            await self.message.clear_reactions()
        except:
            pass
        try:
            await self.remind.delete()
        except:
            pass
        time = f'{datetime.datetime.now().strftime("%a %b %d %I:%M %p")} EST'
        self.message = await channel.send(embed=create_embed('We are being raided!', 'Triggered By:', f'<@{user}>', 'Time', time, '', 'https://bit.ly/2yjmBPY', discord.Color.dark_red(), True))
        await self.message.add_reaction('✅')
        self.count = 0
        self.weewoo_clock = True
        while self.weewoo_clock:
            self.count = 0
            await channel.send('@everyone', delete_after=3)
            await asyncio.sleep(3)
        return True

async def send_top(self, page_num, delete = True):
    channel = self.bot.get_channel(self.channel)
    await channel.trigger_typing()
    offset = page_num*10-10
    list = ''
    top_list = execute_database(f"SELECT minecraft_name,checks FROM walls ORDER BY checks DESC LIMIT 10 OFFSET {offset}")
    for row in top_list:
        offset +=1
        name = row[0]
        checks = row[1]
        name_space  =   '\u202F'*int(18-len(name))
        check_space =   '\u202F'*int(6-len(str(checks)))
        num_space   =   '\u202F'*int(3-len(str(offset)))
        star=get_star(checks, 000)
        if offset <= 5:
            medals = [':first_place:', ':second_place:', ':third_place:', ':medal:', ':medal:']
            medal = medals[offset-1]
        else:
            medal = ''
        list += f'``#{offset}{num_space}-\u202F\u202F{checks}{check_space}{name}{name_space}-``{star}{medal}\n\n'
    try:
        if delete:
            await channel.send(embed=create_medium_embed('Top Checks:', list, 'Get those gold stars your mother never gave you!', discord.Color.dark_gold()), delete_after=20)
        else:
            await channel.send(embed=create_medium_embed('Top Checks:', list, 'Get those gold stars your mother never gave you!', discord.Color.dark_gold()))
    except:
        await channel.send(embed=scripts.error.embed('Page number non-existant', 'Please try a lower page number'), delete_after=10)

async def download_user(ign):
    try:
        #Check if username is in Mojang's database
        url = f'https://api.mojang.com/users/profiles/minecraft/{ign}'
        async with ClientSession() as session:
            async with session.get(url) as response:
                d = await response.json()
                minecraft_id = d['id']
                minecraft_name = d['name']
                return(minecraft_id, minecraft_name)
    except:
        #If username is not in Mojang's database
        return False, False

def add_user_to_database(discord_id, minecraft_id, minecraft_name):
    in_database = execute_database(f"SELECT * FROM walls WHERE discord_id = {discord_id}")
    if not in_database:
        #Adding user if not in database
        execute_database(f"INSERT INTO walls VALUES ('{discord_id}', '{minecraft_id}', '{minecraft_name}', '0')")
    else:
        #Updating user if not in database
        execute_database(f"UPDATE walls SET minecraft_name = '{minecraft_name}', minecraft_id = '{minecraft_id}' WHERE discord_id = {discord_id}")

def check_if_user_in_database(discord_id):
    in_database = execute_database(f"SELECT * FROM walls WHERE discord_id = {discord_id}")
    if not in_database:
        return False
    else:
        return True

def get_user_from_database(discord_id):
    user_info = execute_database(f"SELECT * FROM walls WHERE discord_id = {discord_id}")
    for row in user_info:
        minecraft_id = row[1]
        minecraft_name = row[2]
        checks = row[3]
    return minecraft_id, minecraft_name, checks

def add_check_to_user(discord_id):
    get_count = execute_database(f"SELECT checks FROM walls WHERE discord_id = {discord_id}")
    for row in get_count:
        user_checks = row[0]
    execute_database(f"UPDATE walls SET checks = {user_checks}+1 WHERE discord_id = {discord_id}")

def get_star(count, discord_id):
    stars = execute_database(f"SELECT star FROM stars WHERE count <= {count} ORDER BY count DESC LIMIT 1")
    for row in stars:
        star = row[0]
        return star
    return ('')

def create_embed(title, field1name, field1value, filed2name, filed2value, foot, imageurl, color, inline):
    em = discord.Embed(colour=color)
    em.set_author(name=title, icon_url='https://bit.ly/2CFvJCn') # <-- Nemo Image
    em.add_field(name=field1name, value=field1value, inline=inline)
    em.add_field(name=filed2name, value=filed2value, inline=inline)
    em.set_footer(text=foot)
    em.set_thumbnail(url=imageurl)
    return em

def create_medium_embed(name, value, foot, color):
    em = discord.Embed(colour=color)
    em.add_field(name=name, value=value)
    em.set_footer(text=foot)
    return em

def create_small_embed(description, foot, color):
    em = discord.Embed(description=description, colour=color)
    em.set_footer(text=foot)
    return em

def setup(bot):
    bot.add_cog(Walls(bot))
