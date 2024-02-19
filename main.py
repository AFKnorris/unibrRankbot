import discord
from discord.ext import commands
import aiohttp
import asyncio
import json

# Configuração das intenções
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia mensagens

# Configuração do bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Dicionário com os IDs dos jogadores
profile_data = {
  "284552": "[Fs] Jubileu",
  "2861438": "[Fs] FASTURTLE",
  "1612939": "[Fs] General Enk",
  "910031": "[Fs] SaNgar",
  "3095989": "[Fs] Beringela",
  "2609872": "[Fs] Floripa",
  "6008539": "[Fs] guischmitt",
  "2847988": "[Fs] Reap3r",
  "2064410": "[Fs] NegoDrama",
  "5323486": "[Fs] MK",
  "2178179": "[Fs] Gutera",
  "5281267": "[Fs] vitorluzpoiato",
  "800739": "[Fs] Flamechaos",
  "1636695": "[Fs] ShaDoWn",
  "1297115": "[Fs] 7Mendes",
  "9509227": "[Fs] Black",
  "2460005": "[Fs] Costinha",
  "2294644": "[Fs] Nicolau Mendes",
  "11493774": "[Fs] Mtx",
  "1521490": "[Fs] Hitshangui",
  "2259036": "[Fs] SlicKs",
  "2869032": "[Fs] Xefres",
  "276889": "[Fs] Aquiles",
  "5301298": "[Fs] zWilly",
  "6170464": "[Fs] TchachaBr",
  "10952501": "[Fs] Kawan",
  "1076004": "[Fs] Zero",
  "14450594": "[Fs] JonyBravo",
  "10975290": "[Fs] TheVilly",
  "14332838": "[Fs] Du",
  "4839710": "[Fs] JADSON",
  "1346854": "[Fs] ebenato",
  "6742585": "[Fs] Ricfuria",
  "1868119": "[Fs] Minduca",
  "628948": "[Fs] AgeOfTheKing",
  "222736": "[Fs] MortelentaBr",
  "2324516": "[Fs] Maju",
  "454166": "[Fs] Blinhão",
  "278650": "[Fs] TomaHawk",
  "3369632": "[Fs] Palada",
  "2853675": "[Fs] Cavalo",
  "8990857": "[Fs] hiGhly_",
  "6426073": "[Fs] Seggaty",
  "5419774": "[Fs] dWuino",
  "9754717": "[Fs] Motta",
  "2060448": "[Fs] Rair",
  "10401783": "[Fs] Redykill",
  "1363742": "[Fs] Marques",
  "1596766": "[Fs] ChuracoRS",
  "254049": "[Fs] Andre_Lgc",
  "620649": "[Fs] PoeiraCósmica",
  "2265190": "[Fs] VCTT",
  "811733": "[Fs] Gobbo",
#  "3431528": "[Fs] O_Flexa",
  "5845487": "[Fs] Powerstone",
  "5634777": "[Fs] Glauco",
  "4166548": "[Fs] DrCovid",
  "10833849": "[Fs] Carniça",
  "9900750": "[Fs] Caboclo",
  #    "5319612": "[Fs] Esperando o Mendes"
}

# Lista de resultados - inicialmente vazia
results = []
# Função assíncrona para fazer a solicitação à API e extrair o rating do leaderboard 4
async def get_rating_leaderboard_4(player_id, player_name):
    url = f"https://aoe-api.reliclink.com/community/leaderboard/GetPersonalStat?title=age2&profile_ids=[{player_id}]&leaderboard_id=4"
    retry_count = 3  # Número máximo de tentativas de rechecagem

    while retry_count > 0:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    leaderboard_stats = data.get("leaderboardStats", [])
                    print(f"Player: {player_name}")
                    print(f"Leaderboard Stats: {leaderboard_stats}")
                    normalized_player_name = normalize_name(player_name)  # Normalize o nome do jogador
                    player_rating = -1  # Valor padrão de -1
                    for stat in leaderboard_stats:
                        if stat.get("leaderboard_id") == 4:  # Mudança para leaderboard_id 4
                            player_rating = stat.get("rating")
                            print(f"Rating: {player_rating}")
                            break  # Se encontrou a classificação, sai do loop
                    if player_rating != -1:
                        return {"name": player_name, "rating": player_rating}

        # Se a resposta não for 200, aguarde alguns segundos antes de rechecar
        await asyncio.sleep(5)
        retry_count -= 1

    # Se não foi possível obter um rating após as rechecagens, retorna um dicionário com um valor de classificação padrão de -1
    return {"name": player_name, "rating": -1}

# Comando !rankingtg para acionar a extração de dados do leaderboard_id 4 e exibir os resultados
@bot.command()
async def rankingtg(ctx):
    global results  # Defina results como global

    # Limpar a lista de resultados antes de buscar novamente
    results = []

    # Verificar se todos os perfis em profile_data estão presentes nos resultados
    missing_profiles = [player_name for player_id, player_name in profile_data.items() if player_name not in results]

    # Se houver perfis ausentes, buscar suas classificações
    if missing_profiles:
        async with ctx.typing():
            missing_tasks = [get_rating_leaderboard_4(player_id, player_name) for player_id, player_name in profile_data.items() if player_name in missing_profiles]
            missing_data = await asyncio.gather(*missing_tasks)
            results.extend(missing_data)

    # Ordenar os resultados pelo rating (maior para menor)
    results.sort(key=lambda x: x.get("rating", 0), reverse=True)

    # Título do ranking
    ranking_title = "🏆 Fellow Elo (Team Game) - Ranking:\n"

    # Enviar o título do ranking
    await ctx.send(ranking_title)

    # Enviar os resultados em mensagens divididas
    message_parts = []
    current_message = ""

    for i, result in enumerate(results, start=1):
        rating = result.get("rating", "N/A")
        profile_id = next(key for key, value in profile_data.items() if value == result["name"])
        profile_link = generate_profile_link(profile_id)
        player_info = f"{i}. [{result['name']}]({profile_link}): {rating}\n"

        # Verificar se a próxima mensagem excederá o limite de caracteres (2000 para ser seguro)
        if len(current_message) + len(player_info) >= 2000:
            message_parts.append(current_message)
            current_message = player_info
        else:
            current_message += player_info

    # Adicionar a última parte da mensagem à lista, se houver
    if current_message:
        message_parts.append(current_message)

    # Enviar as mensagens com o ranking
    for part in message_parts:
        await ctx.send(part)
      
# Função assíncrona para fazer a solicitação à API e extrair o rating do leaderboard 3
async def get_rating(player_id, player_name):
  url = f"https://aoe-api.reliclink.com/community/leaderboard/GetPersonalStat?title=age2&profile_ids=[{player_id}]"
  retry_count = 3  # Número máximo de tentativas de rechecagem

  while retry_count > 0:
      async with aiohttp.ClientSession() as session:
          async with session.get(url) as response:
              if response.status == 200:
                  data = await response.json()
                  leaderboard_stats = data.get("leaderboardStats", [])
                  print(f"Player: {player_name}")
                  print(f"Leaderboard Stats: {leaderboard_stats}")
                  normalized_player_name = normalize_name(player_name)  # Normalize o nome do jogador
                  player_rating = -1  # Valor padrão de -1
                  for stat in leaderboard_stats:
                      if stat.get("leaderboard_id") == 3:
                          player_rating = stat.get("rating")
                          print(f"Rating: {player_rating}")
                          break  # Se encontrou a classificação, sai do loop
                  if player_rating != -1:
                      return {"name": player_name, "rating": player_rating}

      # Se a resposta não for 200, aguarde alguns segundos antes de rechecar
      await asyncio.sleep(5)
      retry_count -= 1

  # Se não foi possível obter um rating após as rechecagens, retorna um dicionário com um valor de classificação padrão de -1
  return {"name": player_name, "rating": -1}

# Função para normalizar o nome do jogador
def normalize_name(player_name):
    # Remova caracteres especiais e espaços em branco e converta para letras minúsculas
    return player_name.lower().replace(" ", "").replace("_", "").replace("[", "").replace("]", "")


# Função para gerar o hiperlink para a página de perfil de um jogador
def generate_profile_link(player_id):
    player_name = profile_data.get(player_id, "").replace(" ", "-").replace("_", "-")
    return f"https://www.aoe2insights.com/user/{player_id}"

# Verifica se todos os perfis em profile_data estão na lista de resultados
def verifica_perfis_presentes(results):
    perfis_presentes = set(result["name"] for result in results)
    perfis_profile_data = set(profile_data.values())
    return perfis_presentes == perfis_profile_data

# Comando !ranking para acionar a extração de dados
@bot.command()
async def ranking(ctx):

  global results  # Defina results como global

 # Limpar a lista de resultados antes de buscar novamente
  results = []


  # Verificar se todos os perfis em profile_data estão presentes nos resultados
  missing_profiles = [player_name for player_id, player_name in profile_data.items() if player_name not in results]

  # Se houver perfis ausentes, buscar suas classificações
  if missing_profiles:
      async with ctx.typing():
          missing_tasks = [get_rating(player_id, player_name) for player_id, player_name in profile_data.items() if player_name in missing_profiles]
          missing_data = await asyncio.gather(*missing_tasks)
          results.extend(missing_data)

  # Remover resultados duplicados com base no nome do jogador
  seen_names = set()
  unique_results = []
  for result in results:
      if result["name"] not in seen_names:
          seen_names.add(result["name"])
          unique_results.append(result)

  # Ordenar a lista de resultados únicos pelo rating (maior para menor)
  unique_results = [result for result in unique_results if result is not None]  # Remover resultados None
  unique_results.sort(key=lambda x: x.get("rating", 0), reverse=True)

  # Título do ranking
  ranking_title = "🏆 Fellow Elo (1v1) - Ranking"

  # Enviar o título do ranking
  await ctx.send(ranking_title)

  # Enviar os resultados únicos em mensagens
  ranking_message = ""
  message_parts = []

  for i, result in enumerate(unique_results, start=1):
      rating = result.get("rating", "N/A")
      profile_id = list(profile_data.keys())[list(profile_data.values()).index(result["name"])]
      profile_link = generate_profile_link(profile_id)
      player_info = f"{i}. [{result['name']}]({profile_link}): {rating}\n"

      # Verificar se a mensagem está prestes a exceder o limite de caracteres (1900 para ser seguro)
      if len(ranking_message) + len(player_info) >= 1900:
          message_parts.append(ranking_message)
          ranking_message = player_info
      else:
          ranking_message += player_info

  # Adicionar a última parte da mensagem à lista, se houver
  if ranking_message:
      message_parts.append(ranking_message)

  # Enviar as mensagens com o ranking
  for part in message_parts:
      await ctx.send(part)


# Token do seu bot - substitua com o seu próprio token
TOKEN = 'xxxx'

# Iniciar o bot
bot.run(TOKEN)
