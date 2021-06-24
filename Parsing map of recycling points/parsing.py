import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count

base_url = 'https://recyclemap.ru/?id='


DAYS = ('ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС')


def parse_time_table(table: bs):
    """Парсинг таблицы с временем работы."""
    times = []
    work_time = {}
    for day in table.find_all('td'):
        times.append([day.text[:5], day.text[5:]])
    for day, time_work in zip(DAYS, times):
        if time_work[0] == '':
            time_work = '-'
        work_time[day] = time_work
    return work_time


def parse_html(html: str):
    """Парсинг страницы с пунктом приема."""
    soup = bs(html, 'html.parser')
    try:
        city_chose_id = soup.find('div', class_='main_cityinfo').input['value']
    except:
        return

    # id Каазани - 20
    if city_chose_id != '20':
        return

    try:
        point_head = soup.find('div', class_='point_title').text

        panels = soup.find_all('div', class_='panel_body')

        panel = next(
            x for x in panels if x.find('div', class_='point_address'))

        if not panel:
            return

        point_id = panel.div['data-id']

        point_latitude = panel.div['data-lat']
        point_longitude = panel.div['data-lng']

        point_images_urls = []
        if panel.find('div', class_='point_image'):
            for image_class in panel.find_all('a', class_='popup_image'):
                point_images_urls.append(image_class.img['src'])

        point_rating_val = panel.find('div', class_='point_reiting_val').text
        point_rating_count = panel.find(
            'div', class_='point_reiting_count').text.split()[0]

        trash_types = panel.find(
            'div', class_='point_fractions trash_type sm_trash_type')
        accept_types = [x['data-tooltip'] for
                        x in trash_types.find_all('span')]

        point_address = panel.find(
            'div', class_='point_address').text.strip()

        point_description = panel.find(
            'div', class_='spoiler_inside').text.strip()

        table_time = panel.find('table', class_='time_schem')
        if table_time:
            point_work_time = parse_time_table(table_time)
        else:
            point_work_time = {day: ['00:00', '24:00'] for day in DAYS}

        try:
            point_phone = panel.find('span', class_='phone').text
            point_phone = ''.join(x for x in point_phone if x.isdigit())
        except:
            point_phone = ''

        parsed_point = pd.DataFrame(
            [[point_id, point_head, point_latitude, point_longitude,
              point_address, point_phone,
              point_description, point_images_urls, point_rating_val,
              point_rating_count, accept_types, point_work_time]],
            columns=(
                'id', 'title', 'latitude', 'longitude', 'address', 'contacts',
                'description', 'images_urls', 'rating_value',
                'rating_count', 'accept_types', 'work_time'))

        return parsed_point

    except:
        return None


def get_html(id: int):
    url = base_url + str(id)
    try:
        r = requests.get(url)
    except Exception as e:
        print(e)
        return None
    if r.status_code == 200:
        return r.text
    return None


def parse_page_with_id(id: int):
    print(f'Parsing page of point with id={id}')
    html = get_html(id)
    if html:
        res = parse_html(html)
    else:
        return None
    if res is not None:
        return res


if __name__ == '__main__':
    start_time = time.time()

    result = pd.DataFrame()
    print(f'CPU COUNT = {cpu_count()}')
    ids = list(range(20000, 25000)) + list(range(45000, 50000))
    with Pool(cpu_count() * 2) as pool:
        results = pool.map(parse_page_with_id, ids)

    print("--- %s seconds ---" % (time.time() - start_time))
    # Однопоточный режим 165 точек - 50 секунд
    print('------------RESULTS----------')
    for df in results:
        result = result.append(df)

    print(f'Всего найдено точек в Казани - {len(result)}')

    result.to_excel('result.xlsx')
