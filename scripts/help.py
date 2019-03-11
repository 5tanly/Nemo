# #!/usr/local/bin/python3.7
import discord
import sqlite3

def get_help(option):
    conn = sqlite3.connect('help.db')
    c = conn.cursor()
    c.execute("SELECT * FROM help WHERE command=:command",{'command': option})
    opt = c.fetchall()
    if '[]' in str(opt):
        c.execute("SELECT * FROM help WHERE aliases=:aliases",{'aliases': option})
        opt = c.fetchall()
    for row in opt:
        cmd_name = str(row[0])#.replace('None',':x:')
        cmd_alias = str(row[1])#.replace('None',':x:')
        cmd_desc = str(row[2])#.replace('None',':x:')
        cmd_opt = str(row[3])#.replace('None',':x:')
        cmd_enabled = str(bool(row[4])).replace('False',':x:').replace('True',':white_check_mark:')
    conn.close()
    return(cmd_name, cmd_alias, cmd_desc, cmd_opt)#, cmd_enabled)

def list_commands():
    conn = sqlite3.connect('help.db')
    c = conn.cursor()
    c.execute("SELECT command FROM help ORDER BY command ASC")
    commands = str(c.fetchall()).replace('[(\'','').replace('\',), (\'','\n').replace(',)]','').replace('\'','')
    conn.close()
    return(commands)

def command_help(name, alias, desc, opt):#, enabled):
    em = discord.Embed(colour=0x00aedb)
    em.set_author(name='Help', icon_url='https://bit.ly/2CFvJCn')
    em.add_field(name ='Name:', value=name, inline=False)
    em.add_field(name ='Aliases:', value=alias, inline=False)
    em.add_field(name ='Description:', value=desc, inline=False)
    em.add_field(name ='Options:', value=opt, inline=False)
    #em.add_field(name ='Enabled:', value=enabled, inline=False)
    #em.set_footer(text='Use "?help command" for more info on a command.')
    return em

def command_list(commands):
    em = discord.Embed(colour=0x00aedb)
    em.set_author(name='Help', icon_url='https://bit.ly/2CFvJCn')
    em.add_field(name ='Commands:', value=commands, inline=False)
    em.set_footer(text='Use "!help command" for more info on a command.')
    return em

def command_error(commands):
    em = discord.Embed(colour=0x00aedb)
    em.set_author(name='Help', icon_url='https://bit.ly/2CFvJCn')
    em.add_field(name ='Error:', value='Command ``'+commands+'`` does not exist', inline=False)
    return em

# def setup(bot):
#     bot.add_cog(Help(bot))
