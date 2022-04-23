import requests
import fake_useragent
from bs4 import BeautifulSoup


user_agent = fake_useragent.UserAgent()
header = {"User-Agent": user_agent.chrome}


def get_request(url):
    response = requests.get(url=url, headers=header).text
    return BeautifulSoup(response, "lxml")


def download_image(url):
    return requests.get(url, headers=header).content


def search_manga(manga_name):
    manga_name = manga_name.split()
    soup = get_request(f"https://read.yagami.me/reader/search/?s={'+'.join(manga_name)}")
    search_result = soup.find_all("div", class_="group")
    if not search_result:
        return None
    return search_result


# Собирает
def form_result(search_result):
    manga_links = {}
    for result in search_result:
        manga_link = result.find("a").get("href")
        manga_title = result.find("a").get("title")
        manga_links[manga_title] = manga_link
    return manga_links


# Возвращает словарь {Назва главы : ссылка}
def get_groups(url):
    soup = get_request(url)
    search_result = soup.find_all("div", class_="group")
    if not search_result:
        return None
    all_links = {}
    for element in search_result:
        title = get_volume(element)
        chapters = get_chapters(element)
        all_links[title] = chapters
    return all_links


# Возвращает том или сезон
def get_volume(element):
    title = element.find("div", class_="title").get_text()
    return title if title else "0"


# Возвращает количество глав в томе или главе
def get_chapters(element):
    chapter_links = {}
    chapters = element.find_all("div", class_="element")
    for chapter in chapters:
        link = chapter.find("a").get("href")
        chapter_title = chapter.find("a").get_text()
        chapter_links[chapter_title] = link
    return chapter_links


# Проверка на мангу или манхву
def is_manhva(url):
    page = get_request(url)
    isManhva = page.find("div", class_="topbar_right").get("style")
    return True if isManhva == "display: none;" else False


# Получаем ссылки на все картинки
def get_manhva_image_links(page):
    links = []
    images_blocks = page.find("div", class_="web_pictures").find_all("img")
    for image in images_blocks:
        links.append(image.get("src"))
    # Rework manhva page getter
    return links


# Возвращает номер последней страницы
def get_max_page(page):
    topbar = page.find("div", class_="topbar_right")
    max_page = topbar.find("div", class_="text").get_text()
    max_page = max_page.split()[0]
    return int(max_page)


# Получаем ссилку на картинку манги
def get_manga_image_link(page):
    inner = page.find("div", class_="inner")
    return inner.find("img").get("src")