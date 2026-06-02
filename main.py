import disclib.bot
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    bot = disclib.bot.create_client(prefix="!")
    bot.register_command("clear", bot.clear_commands)
    bot.run(os.getenv("DISCORD_TOKEN"))