import os
from dotenv import load_dotenv
from bot.bot import bot

load_dotenv()

def main():
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main() 