import disclib.bot
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    bot = disclib.bot.create_client(prefix="!", illegal_words=["<@865907695609053216>"])
    bot.run(os.getenv("DISCORD_TOKEN"))