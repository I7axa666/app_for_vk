import requests
import json
from settings import TOKEN_VK
import time
from tqdm import tqdm
import os
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build

def start():

    VK_URL = 'https://api.vk.com/method/photos.get'
    YA_URL = 'https://cloud-api.yandex.net'
    SERVICE_ACCOUNT_FILE = 'my-project-85763-370809-d10118a78a87.json'

    myphoto = []
    photo_list = []

    user_id = input("Введите user id?: ")
    if user_id == "":
        user_id = '1'
    album_id = input("Какие фото загружать wall, profile, saved?: ")
    if album_id == "":
        album_id = 'wall'

    num_of_photo = input("Количество фото для загрузки: ")
    if num_of_photo == '':
        num_of_photo = 5
    else:
        num_of_photo = int(num_of_photo)
    disk = input("Куда сохраняем 1 - яндекс, 2 - гуггл?: ")
    if disk == '':
        disk = '2'
    elif disk == '1':
        token_disk = input("Токен диска?: ")
        while token_disk == "":
            token_disk = input("Токен диска?: ")
    if disk == '2':
        folder_id = input('ведите ID папки на диске, куда сохранить файл')
        if folder_id == '':
            folder_id = '1_fFxmHEWC-pkiwkpQCIt7HdBmsF0rRzM'

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

    if disk == '1':
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

    else:
        for photo in tqdm(photos):
            with open(photo_list[photos.index(photo)], 'wb') as handle:
                response = requests.get(photo['sizes'][-1]['url'], stream=True)

                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

            # folder_id = '1_fFxmHEWC-pkiwkpQCIt7HdBmsF0rRzM'
            file_metadata = {
                'name': photo_list[photos.index(photo)],
                'parents': [folder_id]
            }
            media = MediaFileUpload(photo_list[photos.index(photo)], resumable=True)
            SCOPES = ['https://www.googleapis.com/auth/drive']
            credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('drive', 'v3', credentials=credentials)
            res = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            time.sleep(1)
    for photo in photo_list:
        os.remove(photo)
if __name__ == '__main__':
    start()
