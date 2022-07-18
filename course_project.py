import json
import requests
from tqdm import tqdm
from Get_Token import get_token
from pprint import pprint

class VK_Photo:

    def __init__(self, id, token):
        self.id = id
        self.token = token

    def get_profile_info(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'user_ids': self.id,
                  'access_token': self.token,
                  'v': '5.131',
                  'owner_id': self.id,
                  'album_id': 'profile',
                  'extended': '1'}
        response = requests.get(url=url, params=params).json()
        return response

    def get_photo(self, quantity=5):
        photos_info = {}
        name = ''
        for photos in self.get_profile_info().get('response').get('items'):
            for photo in photos.get('sizes'):
                if photo.get('type') == 'w':
                    # pprint(photo.get('url'))
                    photos_info[name] = photo.get('url'), 'w'
                    photos_info.setdefault(name)
            if photos.get('likes').get('count') not in photos_info:
                name = str(photos['likes']['count']) + '.jpg'
            else:
                name = str(photos['date']) + '.jpg'
                photos_info.setdefault(photos['date'])
        if quantity > len(photos_info):
            print(f'{quantity} слишком большое количество фото, максимальное количество фото {len(photos_info)}')
            exit()
        return photos_info

class YaUploader:

    def __init__(self, token):
        self.token = token
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        self.headers = {
            'Authorization': f'OAuth {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def create_folder(self, name):
        self.name = name
        params = {'path': f'/{name}/'}
        response = requests.put(url=self.url, headers=self.headers, params=params)
        return response

    def uploader(self, files, folder):
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        photos_list = []
        for key, value in tqdm(files.items(), ascii=True, desc='Загрузка: '):
            params = {
                'url': value[0],
                'path': f'{folder}/{key}',
                'disable_redirects': 'true'
            }
            response = requests.post(url=self.url, params=params, headers=self.headers)
            photos_list.append({'file_name': key,
                                'size': value[1]})
            status = response.status_code
            if status < 400:
                tqdm.write(f'\nФото {key} загружено. Статус: {status}')
            else:
                tqdm.write(f'\nЗагрузка не удалась. Статус: {status}')
        with open('data.json', 'a') as file:
            json.dump(photos_list, file, indent=0)
        tqdm.write('Загрузка завершена')

if __name__ == '__main__':
    upload_folder = 'reserve'
    vk = VK_Photo(2736397, get_token('/home/chrnv/PycharmProjects/Homeworks/homeworks/VKtoken.txt'))
    vk.get_profile_info()
    pprint(vk.get_photo(5))
    ya = YaUploader(get_token('/home/chrnv/PycharmProjects/Homeworks/homeworks/YaDisk_token.txt'))
    ya.create_folder(upload_folder)
    ya.uploader(vk.get_photo(13), upload_folder)