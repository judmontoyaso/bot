import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
import openai

# Cargar variables de entorno
load_dotenv()

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True  # Necesario para leer el contenido de los mensajes
bot = commands.Bot(command_prefix='!', intents=intents)

# API de la Biblia
BIBLE_API_URL = "https://www.biblegateway.com/passage/?search="

class OpenAIHelper:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-3.5-turbo"  # Modelo más económico

    def get_verse_explanation(self, verse_text, context=None):
        """Obtiene una explicación del versículo usando OpenAI"""
        prompt = f"""Explica el siguiente versículo bíblico en un solo párrafo:
        
        Versículo: {verse_text}
        
        La explicación debe incluir:
        1. El contexto del versículo (cuándo y por qué se dijo)
        2. El significado principal
        3. Todo en un solo párrafo fluido
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente bíblico que explica versículos incluyendo su contexto y significado en un solo párrafo."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error al obtener explicación de OpenAI: {str(e)}")
            return "Lo siento, no pude generar una explicación en este momento."

    def generate_daily_reflection(self, verse_text):
        """Genera una reflexión diaria basada en un versículo"""
        prompt = f"""Basado en el siguiente versículo, genera una reflexión diaria corta y motivadora:
        
        Versículo: {verse_text}
        
        La reflexión debe ser:
        1. Corta (máximo 2-3 oraciones)
        2. Motivadora
        3. Práctica para aplicar en el día
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente espiritual que ayuda a reflexionar sobre la Palabra de Dios."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error al generar reflexión diaria: {str(e)}")
            return "Lo siento, no pude generar una reflexión en este momento."

@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión!')
    print(f'ID del bot: {bot.user.id}')
    print(f'Conectado a {len(bot.guilds)} servidores')

@bot.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == bot.user:
        return

    print(f'Mensaje recibido: {message.content} de {message.author}')
    
    # Procesar comandos
    await bot.process_commands(message)

@bot.command(name='versiculo')
async def get_verse(ctx, *, reference):
    """
    Obtiene un versículo de la Biblia
    Uso: !versiculo Juan 3:16
    """
    print(f'Comando versículo recibido: {reference}')
    try:
        # Codificar la referencia para la URL
        encoded_reference = reference.replace(' ', '+')
        
        # Hacer la petición a la API
        url = f"{BIBLE_API_URL}{encoded_reference}&version=RVR1960"
        print(f'URL de la API: {url}')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers)
        print(f'Código de respuesta: {response.status_code}')
        
        if response.status_code != 200:
            await ctx.send("Error al obtener el versículo. Por favor, verifica la referencia.")
            return
            
        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar el texto del versículo
        verse_text = soup.find('div', class_='passage-text')
        if not verse_text:
            await ctx.send("No se encontró el versículo solicitado.")
            return
            
        # Limpiar el texto
        verse_text = verse_text.get_text().strip()
        
        # Eliminar el texto adicional
        verse_text = re.sub(r'Read full chapter.*$', '', verse_text, flags=re.IGNORECASE | re.MULTILINE)
        verse_text = re.sub(r'Cross references.*$', '', verse_text, flags=re.IGNORECASE | re.MULTILINE)
        verse_text = re.sub(r'Mateo \d+:\d+ in all Spanish translations.*$', '', verse_text, flags=re.IGNORECASE | re.MULTILINE)
        verse_text = re.sub(r'^\d+\s*', '', verse_text)  # Eliminar números al inicio
        verse_text = re.sub(r'\([A-Z]\)', '', verse_text)  # Eliminar letras entre paréntesis
        verse_text = verse_text.strip()
        
        # Crear el embed
        embed = discord.Embed(
            title=f"📖 {reference}",
            description=verse_text,
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)
        
    except requests.exceptions.RequestException as e:
        print(f'Error de conexión: {str(e)}')
        await ctx.send("Error al conectar con la API de la Biblia. Por favor, intenta más tarde.")
    except Exception as e:
        print(f'Error inesperado: {str(e)}')
        await ctx.send("Ocurrió un error inesperado. Por favor, intenta más tarde.")

# Ejecutar el bot
bot.run(os.getenv('DISCORD_TOKEN')) 