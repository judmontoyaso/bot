import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database.db import Database
from ai.openai_helper import OpenAIHelper
from bible.bible_helper import BibleHelper
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import random

load_dotenv()

class BiblotBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.db = Database()
        self.ai_helper = OpenAIHelper()
        self.bible_helper = BibleHelper()
        
        # Inicializar ChatterBot con configuración mejorada
        self.chatbot = ChatBot(
            'Biblot',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database_uri='sqlite:///database.sqlite3',
            logic_adapters=[
                {
                    'import_path': 'chatterbot.logic.BestMatch',
                    'default_response': 'Lo siento, no entiendo completamente. ¿Podrías reformular tu pregunta?',
                    'maximum_similarity_threshold': 0.90
                },
                {
                    'import_path': 'chatterbot.logic.MathematicalEvaluation'
                },
                {
                    'import_path': 'chatterbot.logic.TimeLogicAdapter'
                }
            ],
            preprocessors=[
                'chatterbot.preprocessors.clean_whitespace',
                'chatterbot.preprocessors.convert_to_ascii',
                'chatterbot.preprocessors.unescape_html'
            ]
        )
        
        # Remover el entrenamiento estático y agregar un método más dinámico
        self.train_dynamic_responses()
        
    def train_dynamic_responses(self):
        """Método para entrenar el bot con respuestas más dinámicas"""
        trainer = ListTrainer(self.chatbot)
        
        # Categorías de conversación
        religious_conversations = [
            ["¿Qué es la fe?", 
             "La fe es la confianza y creencia en Dios y sus promesas, incluso cuando no podemos ver el resultado.",
             "La fe es fundamental en nuestra relación con Dios y se manifiesta en nuestras acciones diarias."],
            ["¿Cómo puedo orar?",
             "La oración es una conversación personal con Dios. Puedes empezar simplemente hablando con Él desde tu corazón.",
             "Jesús nos enseñó a orar en Mateo 6:9-13 con el Padre Nuestro como ejemplo."]
        ]

        bible_study_conversations = [
            ["¿Cómo estudio la Biblia?",
             "Puedes empezar leyendo un capítulo al día y reflexionando sobre su significado.",
             "Te sugiero usar el método SOAP: Scripture (Escritura), Observation (Observación), Application (Aplicación), Prayer (Oración)"],
            ["¿Por dónde empiezo a leer la Biblia?",
             "Muchos recomiendan empezar por el Evangelio de Juan para conocer a Jesús.",
             "También puedes empezar por el libro de Salmos para oraciones y alabanzas."]
        ]

        # Entrenar con cada categoría
        for conversation_set in [religious_conversations, bible_study_conversations]:
            for conversation in conversation_set:
                trainer.train(conversation)

    async def process_chat_response(self, message_content):
        """Procesa la respuesta del chat con múltiples intentos y manejo de errores"""
        try:
            # Primer intento: respuesta directa
            response = self.chatbot.get_response(message_content)
            confidence = response.confidence

            # Si la confianza es baja, intentar con variaciones
            if confidence < 0.5:
                # Intentar con el mensaje simplificado
                simplified = ' '.join(message_content.lower().split())
                alt_response = self.chatbot.get_response(simplified)
                
                # Usar la respuesta con mayor confianza
                if alt_response.confidence > confidence:
                    response = alt_response

            return str(response)
        except Exception as e:
            print(f"Error en el procesamiento del chat: {str(e)}")
            return "Lo siento, tuve un problema procesando tu mensaje. ¿Podrías intentarlo de nuevo?"

    async def on_ready(self):
        print(f'Bot conectado como {self.user.name}')
        await self.change_presence(activity=discord.Game(name="!ayuda para ver comandos"))
        self.add_commands()

    def add_commands(self):
        @self.command(name='privado')
        async def private_message(ctx):
            """Envía un mensaje privado al usuario con instrucciones"""
            try:
                await ctx.author.send("¡Hola! Puedes usar todos los comandos aquí en privado. Algunos ejemplos:\n"
                                    "- `!versiculo Juan 3:16`\n"
                                    "- `!explicar Juan 3:16`\n"
                                    "- `!capitulo Juan 3`\n"
                                    "- `!explicarcapitulo Juan 3`\n"
                                    "- `!reflexion Juan 3:16`\n"
                                    "- `!chatear [mensaje]`")
                if ctx.guild:  # Si el comando se usó en un servidor
                    await ctx.message.add_reaction('✉️')
            except discord.Forbidden:
                await ctx.send("No puedo enviarte mensajes privados. Por favor, habilita los mensajes directos en tus configuraciones de privacidad.")

        @self.command(name='versiculo')
        async def get_verse(ctx, libro, versiculo):
            """Obtiene un versículo específico de la Biblia"""
            try:
                reference = f"{libro} {versiculo}"
                verse_text = await self.bible_helper.get_verse(reference)
                await ctx.send(f"**{reference}**\n{verse_text}")
            except Exception as e:
                await ctx.send(f"Error al obtener el versículo: {str(e)}")

        @self.command(name='explicar')
        async def explain_verse(ctx, libro, versiculo):
            """Explica un versículo específico"""
            try:
                reference = f"{libro} {versiculo}"
                verse_text = await self.bible_helper.get_verse(reference)
                explanation = self.ai_helper.get_verse_explanation(verse_text)
                await ctx.send(f"**{reference}**\n{verse_text}\n\n**Explicación:**\n{explanation}")
            except Exception as e:
                await ctx.send(f"Error al explicar el versículo: {str(e)}")

        @self.command(name='capitulo')
        async def get_chapter(ctx, libro, capitulo):
            """Obtiene un capítulo completo de la Biblia"""
            try:
                reference = f"{libro} {capitulo}"
                chapter_text = await self.bible_helper.get_chapter(reference)
                
                # Dividir el texto en partes si es muy largo
                max_length = 1900  # Límite de Discord es 2000
                parts = [chapter_text[i:i+max_length] for i in range(0, len(chapter_text), max_length)]
                
                await ctx.send(f"**{reference}**")
                for part in parts:
                    await ctx.send(part)
            except Exception as e:
                await ctx.send(f"Error al obtener el capítulo: {str(e)}")

        @self.command(name='explicarcapitulo')
        async def explain_chapter(ctx, libro, capitulo):
            """Explica un capítulo completo de la Biblia"""
            try:
                reference = f"{libro} {capitulo}"
                chapter_text = await self.bible_helper.get_chapter(reference)
                explanation = self.ai_helper.get_chapter_explanation(chapter_text)
                
                # Dividir la explicación en partes si es muy larga
                max_length = 1900
                parts = [explanation[i:i+max_length] for i in range(0, len(explanation), max_length)]
                
                await ctx.send(f"**Explicación de {reference}**")
                for part in parts:
                    await ctx.send(part)
            except Exception as e:
                await ctx.send(f"Error al explicar el capítulo: {str(e)}")

        @self.command(name='reflexion')
        async def daily_reflection(ctx, *, args=None):
            """Genera una reflexión sobre un versículo. Si no se especifica libro ni versículo, genera una reflexión aleatoria."""
            try:
                if args is None:
                    # Lista de libros populares de la Biblia
                    libros = [
                        # Evangelios
                        "Mateo", "Marcos", "Lucas", "Juan",
                        # Cartas de Pablo
                        "Romanos", "1 Corintios", "2 Corintios", "Gálatas", 
                        "Efesios", "Filipenses", "Colosenses", "1 Tesalonicenses",
                        "2 Tesalonicenses", "1 Timoteo", "2 Timoteo", "Tito", "Filemón",
                        # Cartas Generales
                        "Hebreos", "Santiago", "1 Pedro", "2 Pedro", 
                        "1 Juan", "2 Juan", "3 Juan", "Judas",
                        # Libros de Sabiduría
                        "Salmos", "Proverbios", "Eclesiastés", "Cantares",
                        # Profetas
                        "Isaías", "Jeremías", "Lamentaciones", "Ezequiel", "Daniel",
                        "Oseas", "Joel", "Amós", "Abdías", "Jonás", "Miqueas",
                        "Nahum", "Habacuc", "Sofonías", "Hageo", "Zacarías", "Malaquías",
                        # Libros Históricos
                        "Josué", "Jueces", "Rut", "1 Samuel", "2 Samuel",
                        "1 Reyes", "2 Reyes", "1 Crónicas", "2 Crónicas",
                        "Esdras", "Nehemías", "Ester",
                        # Apocalipsis
                        "Apocalipsis"
                    ]
                    libro = random.choice(libros)
                    # Generar un capítulo aleatorio (1-21 para la mayoría de los libros)
                    capitulo = random.randint(1, 21)
                    # Generar un versículo aleatorio (1-30 para la mayoría de los capítulos)
                    versiculo = f"{capitulo}:{random.randint(1, 30)}"
                else:
                    partes = args.split()
                    if len(partes) < 2:
                        await ctx.send("Por favor, proporciona el libro y el versículo (ejemplo: !reflexion Juan 3:16)")
                        return
                    libro = partes[0]
                    versiculo = partes[1]
                
                reference = f"{libro} {versiculo}"
                verse_text = await self.bible_helper.get_verse(reference)
                reflection = self.ai_helper.generate_daily_reflection(verse_text)
                await ctx.send(f"**Reflexión sobre {reference}**\n{verse_text}\n\n{reflection}")
            except Exception as e:
                await ctx.send(f"Error al generar la reflexión: {str(e)}")

        @self.command(name='ayuda')
        async def help_command(ctx):
            """Muestra la lista de comandos disponibles"""
            ayuda_texto = """
**Comandos disponibles:**
- `!versiculo <libro> <capitulo:versiculo>` - Muestra un versículo específico
- `!explicar <libro> <capitulo:versiculo>` - Explica un versículo específico
- `!capitulo <libro> <capitulo>` - Muestra un capítulo completo
- `!explicarcapitulo <libro> <capitulo>` - Explica un capítulo completo
- `!reflexion <libro> <capitulo:versiculo>` - Genera una reflexión sobre un versículo
- `!nota <libro> <capitulo:versiculo> <nota>` - Añade una nota personal a un versículo
- `!misnotas` - Muestra todas tus notas guardadas
- `!privado` - Envía instrucciones por mensaje privado
- `!ayuda` - Muestra este mensaje de ayuda

**Ejemplos:**
- `!versiculo Juan 3:16`
- `!explicar Génesis 1:1`
- `!capitulo Salmos 23`
- `!explicarcapitulo Juan 3`
- `!reflexion Proverbios 3:5`
- `!nota Juan 3:16 Esta es mi nota personal`
- `!misnotas`
"""
            await ctx.send(ayuda_texto)

        @self.command(name='nota')
        async def add_note(ctx, libro, versiculo, *, nota):
            """Añade una nota personal a un versículo"""
            try:
                # Verificar el formato de capítulo:versículo
                if ':' not in versiculo:
                    await ctx.send("Por favor, usa el formato correcto: libro capítulo:versículo nota")
                    return
                    
                chapter, verse = versiculo.split(':')
                
                try:
                    chapter = int(chapter)
                    verse = int(verse)
                except ValueError:
                    await ctx.send("El capítulo y versículo deben ser números")
                    return
                
                # Obtener el versículo primero
                reference = f"{libro} {chapter}:{verse}"
                verse_text = await self.bible_helper.get_verse(reference)
                
                # Guardar la nota en la base de datos
                user_id = self.db.get_or_create_user(str(ctx.author.id), ctx.author.name)
                self.db.add_note(user_id, libro, chapter, verse, verse_text, nota)
                
                # Crear el embed con el versículo y la nota
                embed = discord.Embed(
                    title=f"📝 Tu nota para {reference}",
                    color=discord.Color.green()
                )
                embed.add_field(name="Versículo", value=verse_text, inline=False)
                embed.add_field(name="Tu nota", value=nota, inline=False)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"Error al guardar la nota: {str(e)}")

        @self.command(name='misnotas')
        async def get_notes(ctx):
            """Muestra todas las notas guardadas del usuario"""
            try:
                user_id = self.db.get_or_create_user(str(ctx.author.id), ctx.author.name)
                notes = self.db.get_user_notes(user_id)
                
                if not notes:
                    embed = discord.Embed(
                        title="📝 Tus Notas",
                        description="No tienes notas guardadas todavía.\n\n"
                                  "Usa el comando `!nota` para guardar una nota.",
                        color=discord.Color.blue()
                    )
                    await ctx.send(embed=embed)
                    return
                
                # Crear el embed con las notas
                embed = discord.Embed(
                    title=f"📝 Tus Notas ({len(notes)})",
                    color=discord.Color.blue()
                )
                
                for i, note_data in enumerate(notes):
                    try:
                        note = str(note_data[0]) if note_data[0] else "Sin contenido"
                        created_at = str(note_data[1]) if len(note_data) > 1 else "Sin fecha"
                        book = str(note_data[2]) if len(note_data) > 2 else "Sin libro"
                        chapter = str(note_data[3]) if len(note_data) > 3 else "?"
                        verse = str(note_data[4]) if len(note_data) > 4 else "?"
                        
                        embed.add_field(
                            name=f"{i+1}. {book} {chapter}:{verse}",
                            value=f"{note}\n*Guardado el {created_at}*",
                            inline=False
                        )
                    except Exception as e:
                        embed.add_field(
                            name=f"Error en nota {i+1}",
                            value=str(e),
                            inline=False
                        )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"Error al obtener las notas: {str(e)}")

        @self.command(name='chatear')
        async def chat(ctx, *, message):
            """Chatea con el bot usando IA"""
            try:
                # Obtener respuesta del ChatterBot
                response = await self.process_chat_response(message)
                
                # Crear embed para la respuesta
                embed = discord.Embed(
                    #title="🤖 Respuesta del Bot",
                    description=response,
                    color=discord.Color.blue()
                )
                
                await ctx.send(embed=embed)
            except Exception as e:
                print(f"Error en chat: {str(e)}")
                await ctx.send("Lo siento, hubo un error al procesar tu mensaje.")

    async def on_message(self, message):
        # Ignorar mensajes del propio bot
        if message.author == self.user:
            return

        # Procesar comandos si empiezan con !
        if message.content.startswith('!'):
            ctx = await self.get_context(message)
            if ctx.command:
                await self.invoke(ctx)
        # Si no es un comando y el mensaje es para el bot
        elif self.user in message.mentions or isinstance(message.channel, discord.DMChannel):
            try:
                async with message.channel.typing():
                    response = await self.process_chat_response(message.content)
                    
                embed = discord.Embed(
                    description=response,
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)
            except Exception as e:
                print(f"Error en el manejo del mensaje: {str(e)}")

# Crear la instancia del bot
bot = BiblotBot()

def main():
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main() 