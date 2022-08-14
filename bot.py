from cProfile import run
import os
import asyncio
from typing import Optional
import motor

from beanie import Indexed, init_beanie
from naff import Client, Intents, listen, Embed, InteractionContext, AutoDefer
from utils.customchecks import *
import database as db
from naff.client.errors import NotFound
from naff.api.events.discord import GuildLeft

intents = Intents.ALL
# ad = AutoDefer(enabled=True, time_until_defer=1)

class CustomClient(Client):
    def __init__(self):
        super().__init__(
            intents=intents, 
            sync_interactions=True, 
            delete_unused_application_cmds=True, 
            default_prefix='+', 
            fetch_members=True, 
            # auto_defer=ad,
            # asyncio_debug=True
        )
        self.db: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.models = list()

    async def startup(self):
        for filename in os.listdir('./extensions'):
            if filename.endswith('.py') and not filename.startswith('--'):
                self.load_extension(f'extensions.{filename[:-3]}')
                print(f'grew {filename[:-3]}')
        await db.connect_db()
        await self.astart(os.environ['sml_token'])
    
    @listen()
    async def on_ready(self):
        print(f"[Logged in]: {self.user}")
        guild = self.get_guild(435038183231848449)
        channel = guild.get_channel(932661537729024132)
        await channel.send(f'[Logged in]: {self.user}')

    @listen()
    async def on_guild_join(self, event):
        #add guild to database
        if await db.prefixes.find_one({'guildid':event.guild.id}) is None:
            await db.prefixes(guildid=event.guild.id, prefix='p.').insert()
            guild = self.get_guild(435038183231848449)
            channel = guild.get_channel(932661537729024132)
            await channel.send(f'I was added to {event.guild.name}|{event.guild.id}')
    
    @listen()
    async def on_guild_leave(self, event:  GuildLeft):
        for document in self.models:
            async for entry in document.find({'guildid': event.guild_id}):
                await entry.delete()
            async for entry in document.find({'guild_id': event.guild_id}):
                await entry.delete()
        print(f'Guild {event.guild_id} was removed.')

    async def on_command_error(self, ctx: InteractionContext, error:Exception):
        if isinstance(error, MissingPermissions):
            embed = Embed(description=f":x: {ctx.author.mention} You don't have permissions to perform that action",
                          color=0xdd2e44)
            await ctx.send(embed=embed, ephemeral=True)

        if isinstance(error, RoleNotFound):
            embed = Embed(description=f":x: Couldn't find that role",
                          color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)

        if isinstance(error, UserNotFound):
            embed = Embed(description=f":x: User is not a member of this server ",
                          color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)

        if isinstance(error, CommandOnCooldown):
            embed = Embed(
                description=f":x: Command **{ctx.invoked_name}** on cooldown, try again later.",
                color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
    
    def add_model(self, model):
        self.models.append(model)

bot = CustomClient()
# asyncio.run(bot.startup())