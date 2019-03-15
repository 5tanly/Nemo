#!/usr/local/bin/python3.7
import discord
from discord.ext import commands
import random
import re
import scripts.error
import os
import json
from aiohttp import ClientSession
from random import randint

class randomCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ddos')
    async def ddos(self, ctx, user=''):
        if not user:
            await ctx.send(embed=scripts.error.embed('Invalid IP', 'Please enter a valid IP'), delete_after=10)
            ctx.command.reset_cooldown(ctx)
        else:
            with open (f'{os.getcwd()}/plugins/random/ddos.txt') as t:
                lines  = t.readlines()
                message = random.choice(lines).strip()
            if '<@' in user:
                user = re.sub('[^0-9]', '', user)
                for x in range(1,4):
                    user = user[:x*4] + '.' + user[x*3:]
                user = user[1:]
                user = '{:<14}'.format(user[:14]).replace('5','a').replace('0','b').replace('a','1').replace('b','5')
            else:
                pass
            await ctx.send(message.replace('{}',f'``{user}``'))

    @commands.command(name='namemc')
    async def namemc(self, ctx, ign=''):
        if not ign:
            await ctx.send(embed=scripts.error.embed('Name unavailible', 'Name does not exist as a Minecraft Username on mojang.com'), delete_after=10)
            ctx.command.reset_cooldown(ctx)
        else:
            try:
                #Check if username is in Mojang's database
                url = f'https://api.mojang.com/users/profiles/minecraft/{ign}'
                async with ClientSession() as session:
                    async with session.get(url) as response:
                        d = await response.json()
                        uuid = d['id']
                        url = f'https://api.mojang.com/user/profiles/{uuid}/names'
                        async with ClientSession() as session:
                            async with session.get(url) as response:
                                d = await response.json()
                                message=''
                                for x in d:
                                    message=x['name']+'\n'+message
                                    print(message)
                                skin = f'https://visage.surgeplay.com/face/16/{uuid}?{randint(0, 2304)}'
                                skin_large = f'https://visage.surgeplay.com/frontfull/1040/{uuid}?{randint(0, 2304)}'
                                em = discord.Embed(description=message.replace('_',''), color=discord.Color.dark_teal())
                                em.set_author(name=d[len(d)-1]['name'].replace('_',''), icon_url=skin, url=skin_large)
                                em.set_footer(text='newest - oldest')
                                await ctx.send(embed=em)
            except:
                #If username is not in Mojang's database
                await ctx.send(embed=scripts.error.embed('Name unavailible', 'Name does not exist as a Minecraft Username on mojang.com'), delete_after=10)

    @commands.command(name='reboot', aliases = ['reboots']) # !reboot est, !reboot zombie est, !reboot zombie, !reboot est zombie
    async def reboot(self, ctx, v1='', v2=''):
        await ctx.message.delete()
        reboot_file = json.load(open(os.getcwd()+'/plugins/random/reboots.json'))
        realms = ['skeleton','zombie','blaze','magma','wither','witch','guardian','overlord','chicken','golem', 'cannon']
        timezones = ['pst','est','gmt','cet','aest']
        v1 = v1.lower()
        v2 = v2.lower()
        if v1 in realms:
            server = v1
        elif v2 in realms:
            server = v2
        else:
            server = 'witch'
        if v1 in timezones:
            timezone = v1
        elif v2 in timezones:
            timezone = v2
        else:
            timezone = ''

        if server == 'golem':
            color = discord.Color.dark_grey()
        elif server == 'chicken':
            color = discord.Color.light_grey()
        elif server == 'skeleton':
            color = discord.Color.greyple()
        elif server == 'zombie':
            color = discord.Color.dark_green()
        elif server == 'magma':
            color = discord.Color.dark_orange()
        elif server == 'blaze':
            color = discord.Color.dark_red()
        elif server == 'witch':
            color = discord.Color.dark_purple()
        elif server == 'wither':
            color = discord.Color.default()
        elif server == 'guardian':
            color = discord.Color.dark_teal()
        elif server == 'cannon':
            color = discord.Color.dark_orange()
        elif server == 'overlord':
            color = discord.Color.red()
        elif server == 'hub':
            color = discord.Color.dark_blue()
        else:
            color = discord.Color.blue()

        if timezone:
            message = ''
            times = reboot_file[server][timezone]
            for t in times:
                message += f'{t}\n'
            em = discord.Embed(color=color)
            em.add_field(name=server.capitalize(), value=message)
            em.set_footer(text=timezone.upper())
            await ctx.send(embed=em)
        else:
            message = ''
            tzs = reboot_file[server]
            em = discord.Embed(description=server.capitalize(), color=color)
            for tz in tzs:
                for t in tzs[tz]:
                    message += f'{t}\n'
                em.add_field(name=tz.upper(), value=message, inline=False)
                message = ''
            await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(randomCog(bot))
