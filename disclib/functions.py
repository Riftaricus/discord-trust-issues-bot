import discord

async def ping(message: discord.Message):
    await message.channel.send("Pong")
async def test(message: discord.Message):
    await message.channel.send("Test complete!")