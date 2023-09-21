from pprint import pprint
from urllib.parse import urlencode, quote_plus
import requests
from datetime import date
import time
import tqdm
import json



class VK_get_photo:
    API_base_url = 'https://api.vk.com/method'
    app_id = '51732900'

    def __init__(self, user_id):
        self.token = ''
        self.user_id = user_id
        self.file_dict = {}

    def get_token(self):
        oauth_base_url = 'https://oauth.vk.com/authorize'

        params = {
            'client_id': self.app_id,
            'redirect_uri': 'https://oauth.vk.com/blank.html',
            'display': 'page',
            'scope': 'photos, status, audio',
            'response_type': 'token'
        }

        oauth_url = f'{oauth_base_url}?{urlencode(params, doseq=False, safe="", encoding=None, errors=None, quote_via=quote_plus)}'
        return oauth_url
        self.token = input('Input your VK_token:')
    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }

    def get_prof_photos(self):
        self.token = input('Input your token:')
        params = self.get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': ['profile', 'wall'], 'extended': 1, 'rev': 0})
        response = requests.get(f'{self.API_base_url}/photos.get', params=params)
        print(response.status_code)
        info = response.json()
        # pprint(info['response']['count'])
        i = info['response']['items']
        # pprint(i)
        likes = []
        size = []
        link = []
        load_date = []
        for el in i:
            likes.append(str(el['likes']['count']))
            dt_object = date.fromtimestamp(el['date'])
            load_date.append(str(dt_object.strftime("%d%m%Y")))
            self.file_dict['date'] = load_date
            self.file_dict['likes'] = likes
            for s in el['sizes']:
                if s['height'] >= 1200:
                    size.append(s['type'])
                    link.append(s['url'])
                    self.file_dict['size'] = size
                    self.file_dict['url'] = link

        for i in range(len(likes)):
            for j in range(i + 1, len(likes)):
                if likes[i] == likes[j]:
                    likes[i] = likes[i] + '-' + load_date[i]
        self.file_dict['likes'] = likes

        file_name = []
        if info['response']['count'] <=5:
            for i in range(len(self.file_dict['url'])):
                response = requests.get(self.file_dict['url'][i], stream=True)
                print(response.status_code)
                file_name.append(f"{self.file_dict['likes'][i]}.jpg")
                with open(f"{self.file_dict['likes'][i]}.jpg", 'wb') as file:
                    total = int(response.headers.get('content-length', 0))
                    tqdm_params = {'desc': f"скачивается файл: {self.file_dict['likes'][i]}",
                                   'total': total,
                                   'miniters': 1,
                                   'unit': 'it',
                                   'unit_scale': True,
                                   'unit_divisor': 1024,
                                   }
                    with tqdm.tqdm(**tqdm_params) as pb:
                        for chunk in response.iter_content(chunk_size=8192):
                            pb.update(len(chunk))
                            file.write(chunk)
        self.file_dict['file_name'] = file_name

class Ya_disc:
    base_url = 'https://cloud-api.yandex.net'
    ya_token = input('input your ya.disc_oauth_token: ')
    folder_name = input('input folder name for upload image\images:')

    def __init__(self):
        self.token = f'OAuth {self.ya_token}'
        self.file_dict = vk_client.file_dict
    def upload_photos(self):
        headers = {'Authorization': self.token}
        params = {'path': self.folder_name}
        response = requests.put(f'{self.base_url}/v1/disk/resources', params=params, headers=headers)
        print(response.status_code)
        for i in tqdm.tqdm(self.file_dict['file_name']):
            params['path'] = f'/{self.folder_name}/{i}'
            response = requests.get(f'{self.base_url}/v1/disk/resources/upload', params=params, headers=headers)
            print(response.status_code)
            path_to_load = response.json().get('href', '')
            with open(f"{i}", 'rb') as file:
                response = requests.put(path_to_load, files={'file': file}, stream=True)
                print(response.status_code)

    def make_JSON_file(self):
        json_dict = {}
        json_dict['file_name'] = self.file_dict['file_name']
        json_dict['size'] = self.file_dict['size']
        with open("json_dict.json", "w") as json_file:
            json.dump(json_dict, json_file)


if __name__ == '__main__':
    # vk_client = VK_get_photo(817676891)
    vk_client = VK_get_photo(input('input your VK_ID:'))
    print(vk_client.get_token())
    vk_client.get_prof_photos()
    ya_disc_upload_photo = Ya_disc()
    ya_disc_upload_photo.upload_photos()
    ya_disc_upload_photo.make_JSON_file()


