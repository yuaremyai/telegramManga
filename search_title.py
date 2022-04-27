import requests
import fake_useragent
from bs4 import BeautifulSoup


class Search:

    def __init__(self):
        user_agent = fake_useragent.UserAgent()
        self.header = {"User-Agent": user_agent.chrome}

    def get_request(self, url):
        response = requests.get(url=url, headers=self.header).text
        return BeautifulSoup(response, "lxml")

    def download_image(self, url):
        return requests.get(url, headers=self.header).content

    def search_manga(self, manga_name):
        manga_name = manga_name.split()
        soup = self.get_request(f"https://read.yagami.me/reader/search/?s={'+'.join(manga_name)}")
        search_result = soup.find_all("div", class_="group")
        if not search_result:
            return None
        return search_result

    def form_result(self, search_result):
        manga_links = {}
        for result in search_result:
            manga_link = result.find("a").get("href")
            manga_title = result.find("a").get("title")
            manga_links[manga_title] = manga_link
        return manga_links

    def get_groups(self, url):
        soup = self.get_request(url)
        search_result = soup.find_all("div", class_="group")
        if not search_result:
            return None
        all_links = {}
        for i, element in enumerate(reversed(search_result)):
            chapters = self.get_chapters(element)
            all_links[i] = chapters
        return all_links

    def get_chapters(self, element):
        chapter_links = {}
        chapters = element.find_all("div", class_="element")
        for chapter in reversed(chapters):
            link = chapter.find("a").get("href")
            chapter_title = chapter.find("a").get_text()
            chapter_links[chapter_title] = link
        return chapter_links

    def is_long_images(self, url):
        page = self.get_request(url)
        is_long = page.find("div", class_="topbar_right").get("style")
        return True if is_long == "display: none;" else False

    def get_long_image_links(self, url):
        response = self.get_request(url)
        links = []
        images_blocks = response.find("div", class_="web_pictures").find_all("img")
        for image in images_blocks:
            links.append(image.get("src"))
        return links

    def get_long_max_page(self, url):
        response = self.get_request(url)
        images_blocks = response.find("div", class_="web_pictures").find_all("img")
        return len(images_blocks)

    def get_small_max_page(self, url):
        response = self.get_request(url)
        topbar = response.find("div", class_="topbar_right")
        max_page = topbar.find("div", class_="text").get_text()
        max_page = max_page.split()[0]
        return int(max_page)

    def get_small_image_link(self, url):
        response = self.get_request(url)
        inner = response.find("div", class_="inner")
        return inner.find("img").get("src")
