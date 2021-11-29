# copied completely wholesale
import discord
import logging
import threading
import pywinauto
from subprocess import Popen, PIPE
import dice
import asyncio
import queue
import datetime
from discord.ext import tasks

# from typing import Iterable, Any, Tuple

# logging into a file called discord.log
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()

callSign = 'k!'

dlg = None
p = None
is_server_on = False
my_queue = queue.Queue()
channel_value = channel_val

def terraria_command(command):
    global dlg
    dlg.type_keys('%s\n{ENTER}' % command, with_spaces=True)


def main():
    bat_location = r"E:\Program Files (x86)\Steam\steamapps\common\\tModLoader"
    global p
    p = Popen('tModLoader64BitServer.exe -config serverconfig.txt', shell=True, cwd=bat_location, stdout=PIPE,
              universal_newlines=True)
    global dlg
    dlg = pywinauto.Desktop(backend="uia")['Run - main.py']


def command_input_filtering(arg):
    if arg.count('password ') >= 1 or arg.count('ban ') >= 1 or arg.count('kick ') >= 1:
        return
    elif arg in {'spread', 'mh-cleanup-pink-tiles', 'mh-mod-call', 'mh-configprint', 'mh-mod-lock-world-toggle',
                 'HEROsAdmin', 'mh-tiles-save'}:
        return
    else:
        terraria_command(arg)


def terraria(command):
    global is_server_on
    # print(command[9:])
    if command[9:] == 'start':
        if is_server_on:
            return "Server is running"
        else:
            main()
            is_server_on = True
            return "Starting up"
    elif is_server_on == False:
        return 'lolnop server off, fuqboi'
    else:
        print(command[9:])
        command_input_filtering(command[9:])
        return 'taken in'


def blocking_function():
    # while True:
    for stdout_line in p.stdout:  # iter(p.stdout.readline, ""):  # copied from stack exchange
        print(repr(stdout_line))
        if stdout_line in {'', '\n'}:
            # await channel.send('empty line')
            continue
        elif stdout_line[:9] in {'Resetting', 'Loading w', 'Loading: ', 'Sandboxin', 'Initializ',
                                 'Settling ', 'Object re','HEROsAdmin',': <Server','Parameter'}:  # being rate-limited by discord lmao
            continue
        elif stdout_line.count('/auth') >= 1 or stdout_line.count('password <pass>') >=1 or stdout_line.count('ban <player>') >=1 or stdout_line.count('ban <player>') >=1:
            continue
        elif stdout_line[:3] in {'mh-','exi'}:
            continue
        else:
            my_queue.put(stdout_line)
            #print(stdout_line[:2])


async def my_background_task():
    await client.wait_until_ready()
    channel = client.get_channel(channel_value)
    threaded = False
    while True:  # ugly, don't know a better idea
        if is_server_on and not threaded:  # ugly w/ while true, but while is_server_on doesn't seem to work
            proc = threading.Thread(target=blocking_function)
            proc.start()
            threaded = True
            print('threaded')
        while is_server_on and not my_queue.empty():
            await channel.send(my_queue.get())
        else:
            await asyncio.sleep(1)

def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time) # days always >= 0

    return (future_exec - now).total_seconds()

async def Lyann_meds():
    await client.wait_until_ready()
    channel = client.get_channel(channel_value)
    while True:
        await asyncio.sleep(seconds_until(20,0))
        acknowledged = False
        print("It is time for Lyann to take her meds")
        member = 'player'
        while not acknowledged:
            await channel.send("{}, take meds".format(member))
            await asyncio.sleep(60)
            if channel.last_message.author.id == 315602626655944705:
                acknowledged = True
                print(channel.last_message)
                print("Lyann has taken meds")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    # print('{0.author}: {0.content}'.format(message))
    if message.author == client.user:
        print('Message from {0.author}: {0.content}'.format(message))
        return

    if message.channel.id == channel_value and is_server_on:
      print('Message in {0.channel} by {0.author}: {0.content}'.format(message))
      if message.content.startswith(callSign):
        terraria_command(message.content[len(callSign):])
      else:
        terraria_command('say {0.author}: {0.content}'.format(message))
      return





    elif message.content.startswith(callSign):
        print('Message from {0.author}: {0.content}'.format(message))
        # print(len(callSign))
        command = message.content[len(callSign):]
        print(command)

        if command.lower()[:8] == 'terraria':
            await message.channel.send(terraria(command))
            #await asyncio.sleep(1)
        elif command.lower() == 'help':
            await message.channel.send('currently, the only commands '
                                       'are:\nt!terraria\nt!help\nt!owo\nt!roll\nt!coinflip')
        elif command.lower() in {'uwu', 'owo'}:
            await message.channel.send('OwO')
        elif command.lower()[:5] == 'roll ':
            # print(roll_dice(command[5:]))
            await message.channel.send(dice.count_die_rolls(command[5:]))
        elif command.lower() in {'coinflip', 'coin'}:
            await message.channel.send(dice.coinflip())
        elif command.lower() == 'server':
            await message.channel.send(is_server_on)
        elif command.lower() == 'clear':
            await message.channel.send('working on ittttt')
        elif command.lower()[:4] == 'try ':
            await message.channel.send(dice.reader(command[4:]))
            await message.channel.send(dice.Shunting_yard(command[4:]))
            await message.channel.send(dice.RPN_interpreter(command[4:]))
        else:
            await message.channel.send('Error, invalid command. If you are sure your correct, contact Tim#5259')
            # print('{0.author}'.format(message))




# process = threading.Thread(target=between_callback, args = '')
# print(process.start)
# process.start()

# async def background():
#    await asyncio.to_thread(callback)
# asyncio.run(background())
client.loop.create_task(my_background_task())
client.loop.create_task(Lyann_meds())

#Lyann_meds.start()

client.run('token')
# print(message)
# if ('people') != '{0.author}'.format(message):
#    await message.channel.send('Hello! I am being worked on :two_hearts:')
