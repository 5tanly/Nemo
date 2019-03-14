#!/usr/local/bin/python3.7

import discord
from discord.ext import commands
import asyncio
import os
import math
import sqlite3

#Custom Imports
import scripts.error
import scripts.help

bot = commands.Bot(command_prefix='!', case_insensitive=True)
bot.remove_command('help')

@bot.command(name='help')
@commands.cooldown(2, 1, commands.BucketType.guild)
async def help(ctx, option=''):
    await ctx.message.delete()
    if option == '':
        await ctx.send(embed=scripts.help.command_list(scripts.help.list_commands()), delete_after=20)
    else:
        try:
            name, alias, desc, opt = scripts.help.get_help(option)
            await ctx.send(embed=scripts.help.command_help(name, alias, desc, opt), delete_after=20)
        except:
            await ctx.send(embed=scripts.help.command_error(option), delete_after = 10)

@bot.event
async def on_command_error(ctx, error):
    print(error)
    await ctx.message.delete()
    if isinstance(error, commands.DisabledCommand):
        return await ctx.send(embed=scripts.error.embed('Disabled Command', 'Command: ``!' + str(ctx.command) + '`` has been disabled.'), delete_after = 10)
    elif isinstance(error, commands.CommandNotFound):
        return await ctx.send(embed=scripts.error.embed('Command not found', 'Command does not exist.'), delete_after = 10)
    elif isinstance(error, commands.NotOwner):
        return await ctx.send(embed=scripts.error.embed('Access denied', 'You do not have the proper permissions to use this command'), delete_after = 10)
    elif isinstance(error, commands.CheckFailure):
        return await ctx.send(embed=scripts.error.embed('Access denied', 'You do not have the proper role to use this command'), delete_after = 10)
    elif isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(embed=scripts.error.embed('Command on Cooldown', 'Please wait '+str(math.ceil(error.retry_after))+' seconds.'), delete_after = 10)
    else:
        print(error)

@bot.event
async def on_ready():
    game = discord.Streaming(name='TNT Detectors: Enabled', url='https://www.twitch.tv/NemoOP')
    await bot.change_presence(activity=game)
    print('------')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    plugin_list = os.listdir(f'{os.getcwd()}/plugins')
    print(plugin_list)

    if __name__ == '__main__':
        for plugin in plugin_list:
            if plugin.endswith('.py'):
                print(plugin)
                plugin = f'plugins.{plugin.replace(".py","")}'
                bot.load_extension(plugin)
                print(f'Plugin {plugin.replace("plugins.","")}.py loaded')
            else:
                pass

with open(f'{os.getcwd()}/token.txt', 'r') as token_file:
    token = token_file.read().strip()
    print(token)

with open(f'{os.getcwd()}/guild.txt', 'r') as guild_file:
    bot.guild_id = int(guild_file.read().strip())

bot.run(token)
