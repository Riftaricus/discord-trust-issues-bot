import discord
import disclib.functions
import inspect
from dotenv import load_dotenv


class DiscordClient(discord.Client):
    def __init__(self, prefix:str = "!", **kwargs):
        super().__init__(**kwargs)
        self.prefix = prefix
        self.commands = [
            {
                "command": "ping",
                "function": disclib.functions.ping
            }
        ]
        
    async def clear_commands(self, message):
        self.commands.clear()
        await message.channel.send("Commands cleared")

    async def on_ready(self):
        print(f"Logged on as {self.user}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        for command in self.commands:
            if message.content.strip().lower().startswith(self.prefix + command["command"]):
                func = command["function"]

                # support sync + async functions
                if inspect.iscoroutinefunction(func):
                    await func(message)
                else:
                    func(message)

    def register_command(self, command: str, func):
        self.commands.append({
            "command": command,
            "function": func
        })


def create_client(prefix: str = "!"):
    intents = discord.Intents.default()
    intents.message_content = True
    return DiscordClient(intents=intents, prefix=prefix)


def run(token: str, prefix: str = "!"):
    client = create_client(prefix=prefix)
    client.run(token)
    return client


if __name__ == "__main__":
    import os
    load_dotenv()
    run(prefix="!", token=os.getenv("DISCORD_TOKEN"))