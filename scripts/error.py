#!/usr/local/bin/python3.7
import discord

def embed(error, note):
    em = discord.Embed(colour=discord.Color.red())
    em.set_author(name='Whoops!', icon_url='https://bit.ly/2CFvJCn')
    em.add_field(name=f'__{error}__', value=note)
    em.set_footer(text='Use !help for more information')
    return em
