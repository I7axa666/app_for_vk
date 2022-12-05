import requests
import json
from settings import TOKEN_VK
import time
from tqdm import tqdm

def start():

    VK_URL = 'https://api.vk.com/method/photos.get'
    YA_URL = 'https://cloud-api.yandex.net'

    myphoto = []
    photo_list = []

    user_id = input("Введите user id?:")
    if user_id == "":
        user_id = '1'
    album_id = input("Какие фото загружать wall, profile, saved?:")
    if album_id == "":
        album_id = 'wall'
    token_disk = input("Токен диска?:")
    while token_disk == "":
        token_disk = input("Токен диска?:")
    num_of_photo = input("Количество фото для загрузки:")
    if num_of_photo == '':
        num_of_photo = 5
    else:
        num_of_photo = int(num_of_photo)

    params_vk_photo = {
        'user_ids': user_id,
        'access_token': TOKEN_VK,
        'v': '5.131',
        'album_id': album_id,
        'extended': 1
    }
    photos = requests.get(VK_URL, params=params_vk_photo).json()['response']['items']

    for photo in photos[:num_of_photo]:
        photo_name = str(photo['likes']['count']) + '.jpg'
        if photo_name in photo_list:
            photo_name = str(photo['date']) + photo_name
        photo_list.append(photo_name)
        photo_size = str(photo['sizes'][-1]['type'])
        myphoto.append({"file_name": photo_name, "size": photo_size})

    json_file = json.dumps(myphoto)
    with open('Список фото.json', 'w', encoding="utf-8") as file:
        file.write(json_file)

    headers = {
        'Accept': 'application/json',
        'Authorization': f'OAuth {token_disk}'
    }
    uri_new_folder = '/v1/disk/resources'
    request = YA_URL + uri_new_folder
    params_creat_folder = {'path': 'Фото с ВК'}
    res = requests.put(request, headers=headers, params=params_creat_folder)

    for photo in tqdm(photos):
        path = '/Фото с ВК/' + photo_list[photos.index(photo)]
        url = photo['sizes'][-1]['url']
        params_push_photo = {'url': url, 'path': path}
        uri_new_upload = '/v1/disk/resources/upload/'
        request = YA_URL + uri_new_upload
        photo_put = requests.post(request, params=params_push_photo, headers=headers)
        time.sleep(1)


if __name__ == '__main__':
    start()
