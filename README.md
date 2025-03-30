# Bot de Versículos Bíblicos para Discord

Este es un bot de Discord que permite obtener versículos de la Biblia mediante comandos simples.

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Token de Discord

## Instalación

1. Clona este repositorio
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```
3. Crea un archivo `.env` y añade tu token de Discord:
```
DISCORD_TOKEN=tu_token_aqui
```

## Configuración de Discord

1. Ve al [Portal de Desarrolladores de Discord](https://discord.com/developers/applications)
2. Crea una nueva aplicación
3. Ve a la sección "Bot" y crea un bot
4. Copia el token del bot y guárdalo en el archivo `.env`
5. Invita el bot a tu servidor usando el generador de invitación en la sección "OAuth2"

## Uso

1. Ejecuta el bot:
```bash
python bot.py
```

2. En Discord, usa el comando:
```
!versiculo [referencia]
```

Ejemplos:
- `!versiculo Juan 3:16`
- `!versiculo Salmos 23:1`
- `!versiculo Romanos 8:28`

## Características

- Obtiene versículos de la Biblia usando la API de Bible.org
- Muestra los versículos en un formato embebido bonito
- Manejo de errores para referencias inválidas
- Interfaz simple y fácil de usar

## Desarrollo Local

Para probar el bot localmente:

1. Instala ngrok:
```bash
npm install -g ngrok
```

2. Inicia el servidor Flask:
```bash
python bot.py
```

3. En otra terminal, inicia ngrok:
```bash
ngrok http 5000
```

4. Usa la URL HTTPS proporcionada por ngrok como webhook en tu cuenta de Twilio 