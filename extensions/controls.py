from datetime import datetime, timedelta, timezone
import os
from naff import Client, Extension, Embed, slash_command, InteractionContext, OptionTypes, listen, ActionRow, Button, ButtonStyles, slash_option, spread_to_rows, Select, SelectOption
import database as db
import math
from naff.api.events.internal import Component
from PIL import Image, ImageDraw
import re
from dateutil.relativedelta import relativedelta

async def canvas_snippet(bot: Client, user: db.users):
    canvas = Image.new("RGBA", (960, 540), 'white')
    draw = ImageDraw.Draw(canvas)
    coords = db.PixelPlace.find_all()
    async for coord in coords:
        draw.point((coord.x, coord.y), fill=coord.colour)
        # draw.rectangle(((coord.x, coord.y),(coord.x, coord.y)), fill=coord.colour, outline='yellow', width=1)
    x = user.position.x-25
    if x < 0:
        x= 0
    y = user.position.y-25
    if y < 0:
        y = 0
    x2 = user.position.x+25
    if x2 > 960:
        x2 = 960
    y2 = user.position.y+25
    if y2 > 540:
        y2 = 540
    crop = canvas.crop((x, y,x2,y2))
    (width, height) = (crop.width*5, crop.height*5)
    crop = crop.resize((width, height), resample=4)
    guild = bot.get_guild(435038183231848449)
    channel = guild.get_channel(1005047872191987892)
    crop.save(f'{user.id}_snippet.png')
    msg = await channel.send(files=f'{user.id}_snippet.png')
    os.remove(f'{user.id}_snippet.png')
    return msg.attachments[0].url

def is_hex_valid(str):
    regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    p = re.compile(regex)
    if(str == None):
        return False
    if(re.search(p, str)):
        return True
    else:
        return False

def controlButtons():
    buttons = [
        Button(
            style=ButtonStyles.BLURPLE,
            emoji='⬅️',
            custom_id='left'
        ),
        Button(
            style=ButtonStyles.BLURPLE,
            emoji='⬆️',
            custom_id='up'
        ),
        Button(
            style=ButtonStyles.BLURPLE,
            emoji='⬇️',
            custom_id='down'
        ),
        Button(
            style=ButtonStyles.BLURPLE,
            emoji='➡️',
            custom_id='right'
        ),
        Button(
            style=ButtonStyles.GREY,
            emoji='🖌️',
            custom_id='draw'
        ),
        Button(
            style=ButtonStyles.BLURPLE,
            emoji='⏪',
            custom_id='fastleft'
        ),
        Button(
            style=ButtonStyles.BLURPLE,
            emoji='⏫',
            custom_id='fastup'
        ),
        Button(
            style=ButtonStyles.BLURPLE,
            emoji='⏬',
            custom_id='fastdown'
        ),
        Button(
            style=ButtonStyles.BLURPLE,
            emoji='⏩',
            custom_id='fastright'
        ),
        Button(
            style=ButtonStyles.GRAY,
            emoji='🔃',
            custom_id='refresh'
        ),
        Select(
            custom_id='colourselect',
            placeholder='Choose a pixel colour',
            options=[
                SelectOption(
                   label='White',
                   value='white' 
                ),
                SelectOption(
                   label='Black',
                   value='black' 
                ),
                SelectOption(
                   label='Blurple',
                   value='#5865F2' 
                ),
                SelectOption(
                   label='Blue',
                   value='#3690ea' 
                ),
                SelectOption(
                   label='Light Blue',
                   value='#51e9f4' 
                ),
                SelectOption(
                   label='Green',
                   value='#57F287' 
                ),
                SelectOption(
                   label='Yellow',
                   value='#FEE75C' 
                ),
                SelectOption(
                   label='Dark Yellow',
                   value='#ffd635' 
                ),
                SelectOption(
                   label='Fuchsia',
                   value='#EB459E' 
                ),
                SelectOption(
                   label='Pink',
                   value='#ff99aa' 
                ),
                SelectOption(
                   label='Purple',
                   value='#811e9f' 
                ),
                SelectOption(
                   label='Red',
                   value='#ED4245' 
                ),
                SelectOption(
                   label='Orange',
                   value='#ffa800' 
                ),
                SelectOption(
                   label='Brown',
                   value='#9c6926' 
                )
            ]
        )
    ]
    components: list[ActionRow] = spread_to_rows(*buttons)
    return components

def buttons_embed(picurl:str):
    embed = Embed(
        title='Canvas Controls',
    )
    scs = '**Canvas Size:** 960x540\n⬅️:Move left by 1 pixel\n➡️:Move right by 1 pixel\n⬆️:Move up by 1 pixel\n⬇️:Move down by 1 pixel\n🖌️:Place down a pixel'
    fcs = '⏪:Move left by 10 pixels\n⏩:Move right by 10 pixels\n⏫:Move up by 10 pixels\n⏬:Move down by 10 pixels\n🔃:Refresh the canvas snippet'
    embed.add_field('Control Schema:', f'{scs}\n\n{fcs}')
    embed.set_image(picurl)
    return embed

class controls(Extension):
    def __init__(self, bot: Client):
        self.bot = bot
    
    @slash_command("start", description="Place your brush to the canvas.")
    async def start(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)
        user = await db.users.get(ctx.author.id)
        if user:
            return await ctx.send(f'You already started.', ephemeral=True)
        await db.users(id=ctx.author.id, position=db.PixelPosition(x=0,y=0,colour='#000000')).insert()
        user = await db.users.get(ctx.author.id)
        cropurl = await canvas_snippet(self.bot, user)
        embed = buttons_embed(cropurl)
        await ctx.author.send(embed=embed, components=controlButtons())
        await ctx.send('Successfully started.', ephemeral=True)
    
    @slash_command("controls", description="Summon the control buttons.")
    async def pixelcontrols(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)
        user = await db.users.get(ctx.author.id)
        if not user:
            return await ctx.send(f'You need to start first.')
        cropurl = await canvas_snippet(self.bot, user)
        embed = buttons_embed(cropurl)
        await ctx.author.send(embed=embed, components=controlButtons())
        await ctx.send('Controls were sent to you.', ephemeral=True)
    
    @slash_command("colour", description="Choose your colour to paint with.")
    @slash_option(name="colour", description="Colour hex code", opt_type=OptionTypes.STRING, required=True)
    async def choose_colour(self, ctx: InteractionContext, colour: str):
        await ctx.defer(ephemeral=True)
        user = await db.users.get(ctx.author.id)
        if not user:
            return await ctx.send(f'You need to start first.')
        if is_hex_valid(colour) is False:
            return await ctx.send(f'{colour} is not a valid colour hex code.')
        user.position.colour = colour
        await user.save()
        await ctx.send(f'Your colour is now changed to {colour}.', ephemeral=True)
    
    @slash_command("teleport", description="Teleport to a a specific coords on the canvas.")
    @slash_option(name="x", description="X coord", opt_type=OptionTypes.INTEGER, required=True)
    @slash_option(name="y", description="Y coord", opt_type=OptionTypes.INTEGER, required=True)
    async def teleport(self, ctx: InteractionContext, x:int, y:int):
        await ctx.defer(ephemeral=True)
        user = await db.users.get(ctx.author.id)
        if not user:
            return await ctx.send(f'You need to start first.')
        if (y < 0) or (y > 540):
            return await ctx.send('Y coords can be minimum 0 and max 540')
        if (x < 0) or (x > 960):
            return await ctx.send('X coords can be minimum 0 and max 960')
        user.position.x = x
        user.position.y = y
        await user.save()
        embed = Embed(description=f'You moved to {x}x{y}.')
        cropurl = await canvas_snippet(self.bot, user)
        embed.set_image(cropurl)
        await ctx.send(embed=embed, ephemeral=True)
    
    @slash_command("stats", description="Your statistics.")
    async def stats(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)
        user = await db.users.get(ctx.author.id)
        if not user:
            return await ctx.send(f'You need to start first.')
        
        current_pixels_placed = await db.PixelPlace.find({'user':ctx.author.id}).count()
        
        embed = Embed(
            title=f'Stats for {ctx.author}'
        )
        embed.add_field('Position:', f'{user.position.x}x{user.position.y}')
        embed.add_field('Colour:', f'{user.position.colour}')
        embed.add_field('Last time you placed a pixel:', f'<t:{math.ceil(user.time.timestamp())}:R>')
        embed.add_field('Current Pixels placed:', current_pixels_placed)
        embed.add_field('Pixels placed:', user.pixels_placed)
        cropurl = await canvas_snippet(self.bot, user)
        embed.set_image(cropurl)
        await ctx.send(embed=embed, ephemeral=True)
    
    @listen()
    async def on_control(self, event: Component):
        daways = ['left', 'right', 'up', 'down', 'fastleft', 'fastright', 'fastup', 'fastdown']
        ctx = event.context
        if ctx.custom_id in daways:
            user = await db.users.get(ctx.author.id)
            if not user:
                return await ctx.send(f'You need to start first.', ephemeral=True)
            if ctx.custom_id == 'up':
                da_way = 'up'
                howmuch = 1
                old_y = user.position.y
                new_y = old_y-1
                user.position.y = new_y
                if (new_y < 0) or (new_y > 540):
                    return await ctx.send('Not possible to move beyond the canvas.', ephemeral=True)
            
            elif ctx.custom_id == 'down':
                da_way = 'down'
                howmuch = 1
                old_y = user.position.y
                new_y = old_y+1
                user.position.y = new_y
                if (new_y < 0) or (new_y > 540):
                    return await ctx.send('Not possible to move beyond the canvas.', ephemeral=True)
            
            elif ctx.custom_id == 'left':
                da_way = 'left'
                howmuch = 1
                old_x = user.position.x
                new_x = old_x-1
                user.position.x = new_x
                if (new_x < 0) or (new_x > 960):
                    return await ctx.send('Not possible to move beyond the canvas.', ephemeral=True)
            
            elif ctx.custom_id == 'right':
                da_way = 'right'
                howmuch = 1
                old_x = user.position.x
                new_x = old_x+1
                user.position.x = new_x
                if (new_x < 0) or (new_x > 960):
                    return await ctx.send('Not possible to move beyond the canvas.', ephemeral=True)
            
            elif ctx.custom_id == 'fastup':
                da_way = 'up'
                howmuch = 10
                old_y = user.position.y
                new_y = old_y-10
                user.position.y = new_y
                if (new_y < 0) or (new_y > 540):
                    return await ctx.send('Not possible to move beyond the canvas.', ephemeral=True)
            
            elif ctx.custom_id == 'fastdown':
                da_way = 'down'
                howmuch = 10
                old_y = user.position.y
                new_y = old_y+10
                user.position.y = new_y
                if (new_y < 0) or (new_y > 540):
                    return await ctx.send('Not possible to move beyond the canvas.', ephemeral=True)
            
            elif ctx.custom_id == 'fastleft':
                da_way = 'left'
                howmuch = 10
                old_x = user.position.x
                new_x = old_x-10
                user.position.x = new_x
                if (new_x < 0) or (new_x > 960):
                    return await ctx.send('Not possible to move beyond the canvas.', ephemeral=True)
            
            elif ctx.custom_id == 'fastright':
                da_way = 'right'
                howmuch = 10
                old_x = user.position.x
                new_x = old_x+10
                user.position.x = new_x
                if (new_x < 0) or (new_x > 960):
                    return await ctx.send('Not possible to move beyond the canvas.', ephemeral=True)
            await user.save()
            
            cropurl = await canvas_snippet(self.bot, user)
            embed = buttons_embed(cropurl)
            await ctx.edit_origin(embed=embed, components=controlButtons())
            await ctx.author.send(f'You moved {da_way} by {howmuch} to {user.position.x}x{user.position.y}.', delete_after=3)
    
    @listen()
    async def on_draw(self, event: Component):
        ctx = event.context
        if ctx.custom_id == 'draw':
            user = await db.users.get(ctx.author.id)
            if user is None:
                return await ctx.send(f'You need to start first.', ephemeral=True)
            if (ctx.author.id != 400713431423909889) and ((user.time+timedelta(minutes=3)) > datetime.now()):
                return await ctx.send(f'You will be able to place another pixel <t:{math.ceil((user.time+timedelta(minutes=3)).timestamp())}:R>', ephemeral=True)
            pixel = await db.PixelPlace.find_one({'x':user.position.x, 'y':user.position.y})
            if not pixel:
                await db.PixelPlace(user=ctx.author.id, x=user.position.x, y=user.position.y, colour=user.position.colour, date=datetime.now()).insert()
            else:
                pixel.colour = user.position.colour
                pixel.date = datetime.now()
                await pixel.save()
            user.time = datetime.now()
            user.pixels_placed = user.pixels_placed+1
            await user.save()
            await ctx.author.send(f'You put a pixel to {user.position.x}x{user.position.y}.', ephemeral=True, delete_after=3)
            cropurl = await canvas_snippet(self.bot, user)
            embed = buttons_embed(cropurl)
            await ctx.edit_origin(embed=embed, components=controlButtons())
    
    @slash_command("screenshot", description="the screenshot of the canvas.")
    async def screenshot(self, ctx: InteractionContext):
        await ctx.defer(ephemeral=True)
        canvas = Image.new("RGBA", (960, 540), 'white')
        draw = ImageDraw.Draw(canvas)
        coords = db.PixelPlace.find_all()
        async for coord in coords:
            draw.point((coord.x, coord.y), fill=coord.colour)
        canvas.save(f'{ctx.author.id}_screenshot.png')
        await ctx.send(f'Enjoy!', ephemeral=True, file=f'{ctx.author.id}_screenshot.png')
        os.remove(f'{ctx.author.id}_screenshot.png')
    
    @listen()
    async def on_colour(self, event: Component):
        ctx = event.context
        if ctx.custom_id == 'colourselect':
            user = await db.users.get(ctx.author.id)
            if user is None:
                return await ctx.send(f'You need to start first.', ephemeral=True)
            for value in ctx.values:
                user.position.colour = value
                await user.save()
                await ctx.send(f'Your colour is now changed to {value}.', ephemeral=True)
    
    @listen()
    async def on_refresh(self, event: Component):
        ctx = event.context
        if ctx.custom_id == 'refresh':
            user = await db.users.get(ctx.author.id)
            if user is None:
                return await ctx.send(f'You need to start first.', ephemeral=True)
            cropurl = await canvas_snippet(self.bot, user)
            embed = buttons_embed(cropurl)
            await ctx.edit_origin(embed=embed, components=controlButtons())
    
    @slash_command(name='botinfo', description="lets me see info about the bot")
    async def botinfo(self, ctx: InteractionContext):
        member = self.bot.user
        cdiff = relativedelta(datetime.now(tz=timezone.utc), member.created_at.replace(tzinfo=timezone.utc))
        creation_time = f"{cdiff.years} Y, {cdiff.months} M, {cdiff.days} D"

        embed = Embed(color=0x5865f2,
                      title=f"Bot Info")
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="ID(snowflake):", value=member.id, inline=False)
        embed.add_field(name="Nickname:", value=member.display_name, inline=False)
        embed.add_field(name="Created account on:", value=f"<t:{math.ceil(member.created_at.timestamp())}> `{creation_time} ago`", inline=False)
        embed.add_field(name="Library:", value="[NAFF](https://naff.info/)")
        embed.add_field(name="Servers:", value=len(self.bot.user.guilds))
        embed.add_field(name="Bot Latency:", value=f"{self.bot.latency * 1000:.0f} ms")
        embed.add_field(name='‎', value='**[GitHub](https://github.com/siren15/d-place)**')
        embed.add_field(name='‎', value='**[Live Canvas](https://dplace.up.railway.app/)**')
        embed.set_footer(text="Melody | powered by NAFF")
        await ctx.send(embed=embed)
    
    @slash_command(name='canvas', description='Check the live canvas!')
    async def leaderboard(self, ctx: InteractionContext):
        components = Button(
            style=ButtonStyles.URL,
            label="Click Me!",
            url=f"https://dplace.up.railway.app/",
        )
        await ctx.send("A button to the website canvas!", components=components)

def setup(bot):
    controls(bot)