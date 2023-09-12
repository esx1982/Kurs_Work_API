from pprint import pprint
from urllib.parse import urlencode, quote_plus
import requests
from datetime import date
import time
import tqdm
import json

token = 'vk1.a.XnY8eUrSIxAiOsoysguL31wWVFF4bxWVYkIN-Ganex-o0c13IfLxY2452lq7M-CMHGcKxaW7GVtmrCVIuLKyaXmGruKG7kHZ05QuGw8NhhPagOt04CHzLjqgDh2v4FPJc9Tq6O-d6LNurugL9V-p1FEKMXrkOl2qxeccV5WfdMf6FuNwhKT9XR3AoUcrr-z-BDbViYkzVRCvHoXEMBZYCA'

def get_token():
    oauth_base_url = 'https://oauth.vk.com/authorize'

    params = {
        'client_id': app_id,
        'redirect_uri': 'https://oauth.vk.com/blank.html',
        'display': 'page',
        'scope': 'photos, status, audio',
        'response_type': 'token'
        }

    oauth_url = f'{oauth_base_url}?{urlencode(params, doseq=False, safe="", encoding=None, errors=None, quote_via=quote_plus)}'
    return oauth_url

class VK_get_photo:
    API_base_url = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id
        self.file_dict = {}
    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }
    def get_status(self):
        params = self.get_common_params()
        params.update({'user_id': self.user_id})
        response = requests.get(f'{self.API_base_url}/status.get', params=params)
        return response.json().get('response', {}).get('text')
    def set_status(self, new_status):
        params = self.get_common_params()
        params.update({'user_id': self.user_id, 'text': new_status})
        response = requests.get(f'{self.API_base_url}/status.set', params=params)
        response.raise_for_status()

    def replace_status(self, target, replace_str):
        status = self.get_status()
        new_status = status.replace(target, replace_str)
        self.set_status(new_status)

    def get_prof_photos(self):
        params = self.get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': ['profile', 'wall'], 'extended': 1, 'rev': 0})
        response = requests.get(f'{self.API_base_url}/photos.get', params=params)
        info = response.json()
        # pprint(info['response']['count'])
        i = info['response']['items']
        # pprint(i)
        # file_dict = {}
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

    def upload_photos(self):
        # params = {}
        base_url = 'https://cloud-api.yandex.net'
        headers = {'Authorization': 'OAuth '}
        params = {'path': 'Image'}
        response = requests.put(f'{base_url}/v1/disk/resources', params=params, headers=headers)
        for i in tqdm.tqdm(self.file_dict['file_name']):
            params['path'] = f'/Image/{i}'
            response = requests.get(f'{base_url}/v1/disk/resources/upload', params=params, headers=headers)
            path_to_load = response.json().get('href', '')
            with open(f"{i}", 'rb') as file:
                response = requests.put(path_to_load, files={'file': file}, stream=True)

    def make_JSON_file(self):
        json_dict = {}
        json_dict['file_name'] = self.file_dict['file_name']
        json_dict['size'] = self.file_dict['size']
        with open("json_dict.json", "w") as json_file:
            json.dump(json_dict, json_file)


if __name__ == '__main__':
    # print(get_token())
    vk_client = VK_get_photo(token, 817676891)
    vk_client.get_prof_photos()
    vk_client.upload_photos()
    vk_client.make_JSON_file()
    # print(vk_client.get_status())
    # vk_client.set_status('Приветули!')
    # vk_client.replace_status
