import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from time import sleep
import random
import os
from copy_file_xml import copy_file

url = 'https://rev-ritter.com/catalog/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
count = 1


def new_file_xml():
    root = ET.Element('products')
    tree = ET.ElementTree(root)
    with open('ritter_pars.xml', 'wb') as file:
        tree.write(file)


def current_id():
    existing_tree = ET.parse('ritter_pars.xml', parser=ET.XMLParser(encoding="utf-8"))
    root = existing_tree.getroot()

    id_elements = root.findall(".//id")

    last_id_element = id_elements[-1]
    last_id = last_id_element.text

    print('=========')
    print('=========')
    print('=========')
    print("Последний элемент id:", last_id)
    print('=========')
    return int(last_id)


def get_html(url):
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def get_catalog():
    soup = get_html(url)
    catalog_element = soup.find_all('li', class_="category-blocks__item")

    for chapter in catalog_element:
        chapter_url = 'https://rev-ritter.com' + chapter.find('a').get('href')
        yield chapter_url


def get_pagination(soup_chapter):
    max_page = soup_chapter.find(class_='js-pagination-controller').get('data-count')
    return max_page


def get_product(card_url, count):
    soup = get_html(card_url)
    params = dict()

    params['id'] = str(count)

    title = soup.find('h1', class_='detail__name').text
    params['title'] = title

    description = soup.find(class_='detail__subtitle').text
    params['description'] = description

    article = soup.find(class_='detail__article').text.replace('Арт. ', "")
    params['article'] = article

    gallery = soup.find_all("img", class_='detail__image-img')
    gallery_list = []
    for gallery_element in gallery:
        gallery_no_empty = "https://rev-ritter.com" + gallery_element.get('src')
        if gallery_no_empty != "https://rev-ritter.com":
            gallery_list.append(gallery_no_empty)
    params['gallery'] = gallery_list

    params['img'] = params['gallery'][0]
    if len(params['gallery']) == 1:
        params['gallery'] = []

    characteristics = soup.find_all(class_="detail__properties-row")
    characteristics_dict = dict()
    for char in characteristics:
        key = char.find_all('span')[0].text
        value = char.find_all('span')[1].text
        characteristics_dict[key] = value
    params['characteristics'] = characteristics_dict

    sleep(random.randint(1, 3))
    return params


def load_in_xmlx(params):
    existing_tree = ET.parse('ritter_pars.xml', parser=ET.XMLParser(encoding="utf-8"))
    root = existing_tree.getroot()

    product = ET.SubElement(root, 'product')

    id = ET.SubElement(product, 'id')
    id.text = params['id']

    title = ET.SubElement(product, 'title')
    title.text = params['title']

    description = ET.SubElement(product, 'description')
    description.text = params['description']

    article = ET.SubElement(product, 'article')
    article.text = params['article']

    brand = ET.SubElement(product, 'brand')
    brand.text = "Ritter"

    img = ET.SubElement(product, 'img')
    img.text = params['img']

    gallery = ET.SubElement(product, "gallery")
    for picture in params['gallery']:
        gallery_element = ET.SubElement(gallery, "gallery_element")
        gallery_element.text = picture

    characteristics = ET.SubElement(product, "characteristics")
    for key, value in params['characteristics'].items():
        char_element = ET.SubElement(characteristics, "char")
        char_element.set('name', key)
        char_element.text = value

    existing_tree.write('ritter_pars.xml', encoding="utf-8", xml_declaration=True)


if not os.path.isfile('ritter_pars.xml'):
    new_file_xml()
    last_id = 0
else:
    last_id = current_id()

for chapter_url in get_catalog():
    print("=================")
    print(f"Chapter {chapter_url}")
    print("=================")

    soup = get_html(chapter_url)
    pages = get_pagination(soup)

    for page in range(1, int(pages) + 1):
        page_url = f"{chapter_url}?PAGEN_2={page}"

        print()
        print(f"Page {page}")
        print()

        soup = get_html(page_url)
        products_card = soup.find_all('a', class_='item-block')

        for product_url in products_card:
            card_url = 'https://rev-ritter.com' + product_url.get("href")

            print(f"Product {count} || {card_url}")
            if count <= last_id:
                count += 1
                continue

            params_dict = get_product(card_url, count)
            load_in_xmlx(params_dict)

            count += 1

    print()

copy_file()
