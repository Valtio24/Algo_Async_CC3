import asyncio
import feedparser
import aiohttp


# Fonction asynchrone qui va chercher un flux RSS
async def parse_feed(session, url):
    try:
        # on fait une requete HTTP GET vers le flux(timeout sert a passer les requetes qui ont une erreur )
        async with session.get(url, timeout=10) as response:
            data = await response.read()  # on lit les donné
            feed = feedparser.parse(data)  # on parse le xml du RSS
            articles = []  # liste où on va stocker les article

            # pour chaque entreae (article) dans le flux
            for entry in feed.entries:
                articles.append({
                    "title": entry.get("title", "N/A"),
                    "link": entry.get("link", "N/A"),
                    "summary": entry.get("summary", ""),
                    "published": entry.get("published", "N/A")
                })

            return articles  # on retourne la liste des articles
    except Exception as e:
        print(f"[!] Erreur sur {url} : {e}")  # en cas de bug on affiche l'erreur
        return []  # on retourne une liste vide si y'a un soucis


# Fonction pour chercher des articles qui contiennent un mot-clé
async def rss_finder(keyword):
    # on lit la liste des URLs RSS dans un fichier texte
    with open('rss_list.txt', 'r', encoding='utf-8') as f:
        rss_urls = [line.strip() for line in f if line.strip()]

    # on ouvre une session HTTP aiohttp
    async with aiohttp.ClientSession() as session:
        tasks = []  # on stocke toutes les taches async à faire

        for url in rss_urls:
            print(f"Looking in {url}")  # affichage juste pour savoir où on cherche
            tasks.append(parse_feed(session, url))  # on prepare les taches

        results = await asyncio.gather(*tasks)  # on lance tout en meme temp

        # on filtre les articles
        for articles in results:
            for article in articles:
                if keyword.lower() in article["title"].lower() or keyword.lower() in article["summary"].lower():
                    print(f"{article['title']} ({article['published']})")
                    print(f"🔗 {article['link']}")


# Mode synchrone (en vrai c’est juste un faux synchrone, on utilise quand meme async)
def final_no_async():
    keyword_1 = input("Bonjour donnez moi un mot-clé : ")
    keyword_2 = input("Donnez  moi un autre mot-clé : ")
    keyword_3 = input("donnez moi un dernier mot-clé : ")

    # on lance chaque recherche une par une (donc pas en paralelle)
    asyncio.run(rss_finder(keyword_3))
    asyncio.run(rss_finder(keyword_2))
    asyncio.run(rss_finder(keyword_1))


# Mode asynchrone : toutes les recherches sont lancees en même temps
async def final():
    keyword_1 = input("Bonjour donnez moi un mot-clé : ")
    keyword_2 = input("Donnez  moi un autre mot-clé : ")
    keyword_3 = input("donnez moi un dernier mot-clé : ")

    # les trois rss_finder sont exécuté en parallele
    await asyncio.gather(
        rss_finder(keyword_1),
        rss_finder(keyword_2),
        rss_finder(keyword_3)
    )


import time


def main():
    y = input("Voulez vous lancer en asynchrone ? ").strip().lower()

    if y == "oui":
        start = time.perf_counter()  # debut chrono
        asyncio.run(final())  # on lance la version async
        end = time.perf_counter()  # fin chrono
        elapsed = end - start
        print(f'Time taken: {elapsed:.6f} seconds')  # affichage du temps

    elif y == "non":
        start = time.perf_counter()
        final_no_async()  # on lance le mode "synchrone"
        end = time.perf_counter()
        elapsed = end - start
        print(f'Time taken: {elapsed:.6f} seconds')

    else:
        print("Je n'ai pas compris la réponse, pouvez vous répondre seulement pour oui ou non ?")
        main()


main()
