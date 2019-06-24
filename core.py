
import discord
from discord.ext import tasks, commands
import os
import asyncio
import json
import aiohttp
from datetime import datetime
import traceback


class MiniGolf(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(command_prefix="mg!", case_insensitive=True, reconnect=True)

        self.token = json.load(open("./data/token.json"))["token"]
        self.owner = 404244659024429056
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.uptime = datetime.now()
        self.loop_presence.start()
        self.toggle = True

    @tasks.loop(seconds=30.0)
    async def loop_presence(self):
        if self.toggle:
            pres = f"mg!help | hey :)"
            self.toggle = False
        else:
            pres = f"mg!help | {len(self.users)} users"
            self.toggle = True

        await self.change_presence(activity=discord.Game(pres))

    @loop_presence.before_loop
    async def before_looper(self):
        print('Waiting...')
        await self.wait_until_ready()

    async def on_ready(self):

        for cog in os.listdir("cogs"):
            try:
                if not cog.endswith(".py"):
                    continue
                self.load_extension(f"cogs.{cog.replace('.py', '')}")
                print(f"Loaded {cog}")
            except:
                print(f"Failed to load {cog}\n{traceback.format_exc()}")

    def run(self):
        super().run(self.token)


MiniGolf().run()
