import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

base_url = 'https://recyclemap.ru/?id='
#id = 46935
#id = 23325
id = 24095
id = 1152

DAYS = ('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС')

url = base_url + str(id)

result = pd.DataFrame()


def parse_time_table(table:bs):
    """Парсинг таблицы с временем работы."""
    times = []
    work_time = {}
    for day in table.find_all('td'):
        times.append([day.text[:5],day.text[5:]])
    for day,time in zip(DAYS, times):
        if time[0]=='':
            time = '-'
        work_time[day]=time
    return work_time

r = requests.get(url)
soup = bs(r.text,'html.parser')
point_head = soup.find('div',class_='point_title')
print(point_head.text)
panels = soup.find_all('div',class_='panel_body')
for panel in panels:
    if not panel.find('div',class_='point_address'):
        continue
    point_id = panel.div['data-id']

    point_latitude = panel.div['data-lat']
    point_longitude = panel.div['data-lng']
    print(point_latitude, point_longitude)

    point_images_urls = []
    if panel.find('div',class_='point_image'):
        for image_class in panel.find_all('a',class_='popup_image'):
            point_images_urls.append(image_class.img['src'])
    print(point_images_urls)

    point_reiting_val = panel.find('div', class_='point_reiting_val').text
    point_reiting_count = panel.find('div', class_='point_reiting_count').text.split()[0]
    print('Raiting',point_reiting_val,point_reiting_count)

    trash_types = panel.find('div',class_='point_fractions trash_type sm_trash_type')
    accept_types = [x['data-tooltip'] for x in trash_types.find_all('span')]
    print(accept_types)

    point_address = panel.find('div', class_='point_address').text.strip()
    print(point_address)

    point_description = panel.find('div',class_='spoiler_inside').text.strip()
    print(point_description)

    table_time = panel.find('table',class_='time_schem')
    if table_time:
        point_work_time = parse_time_table(table_time)
    else:
        point_work_time = {day:['00:00','24:00'] for day in DAYS}
    print(point_work_time)

