import os
import sys

# Añadir el directorio actual al PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.bot.bot import bot
from dotenv import load_dotenv

load_dotenv()

# Obtener el token desde las variables de entorno
TOKEN = os.getenv('DISCORD_TOKEN')

if __name__ == "__main__":
    bot.run(TOKEN) 