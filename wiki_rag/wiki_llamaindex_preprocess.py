import requests
import os
import shutil
from tqdm import tqdm
import html2text
from bs4 import BeautifulSoup

cut_offs = ["##  Gallery", "##  Trivia", "##  References"]

def main():
    save_dir = "glados_knowledge/"

    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)

    os.mkdir(save_dir)

    url_file = open("urls.txt", 'r')
    url_list = url_file.readlines()
    url_file.close()

    for url in tqdm(url_list):
        r = requests.get(url.strip())

        soup = BeautifulSoup(r.text, 'html.parser')

        title = soup.find_all('title')[0].get_text()
        title = title.replace(" - Portal Wiki", "")
        content = soup.find_all("div", {"id": "mw-content-text"})[0]

        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_tables = True

        outFile = open(save_dir + title + ".md", 'w')
        outFile.write(h.handle(content.prettify()))

        outFile.close()

    for file in tqdm(os.listdir(save_dir)):
        inFile = open(save_dir + file, 'r')
        lines = inFile.readlines()
        inFile.close()

        outFile = open(save_dir + file, 'w')

        for line in lines:
            if line.strip() in cut_offs:
                break
            
            outFile.write(line)

        outFile.close()

main()

