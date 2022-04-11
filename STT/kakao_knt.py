import requests
from socket import error as SocketError
import errno
import os 
import json
from requests_toolbelt.multipart import decoder

def knt(audio_dir):
    api_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
    headers = {
        # "Transfer-Encoding": "chunked",
        "Content-Type": "application/octet-stream",
        "Authorization": "KakaoAK a3318b18dd1894c9217c299826dda5fb",
    }
    chunked_headers = {
        "Transfer-Encoding": "chunked",
        "Content-Type": "application/octet-stream",
        "Authorization": "KakaoAK a3318b18dd1894c9217c299826dda5fb",
    }

    for audio_file_name in os.listdir(audio_dir):
        audio_path = os.path.join(audio_dir, audio_file_name)
        audio_file = open(audio_path, 'rb')
        files = {'file': audio_file}

        try:
            response = requests.post(api_url, headers=headers, files=files)

            print("audio name = ",audio_file_name)
            # with file
            print("status code = ", response.status_code)
            if response.status_code == 413:
                response = requests.post(api_url, headers=chunked_headers, files=files)

            # print(response.text)
            print("plain text")
            print(response.text)
            multipart_data = decoder.MultipartDecoder.from_response(response, encoding='utf-8')
            
            # for part in multipart_data.parts:
            #     print(part.text)

            print(json.loads(multipart_data.parts[-1].text))
                
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise
            else:
                headers = {
                    "Transfer-Encoding": "chunked",
                    "Content-Type": "application/octet-stream",
                    "Authorization": "KakaoAK a3318b18dd1894c9217c299826dda5fb",
                }

                response = requests.post(api_url, headers=headers, files=files)

                print(response.status_code)
                print(response.text)

# curl -v -X POST "https://kakaoi-newtone-openapi.kakao.com/v1/recognize" \
# -H "Transfer-Encoding: chunked" \
# -H "Content-Type: application/octet-stream" \
# -H "Authorization: KakaoAK a3318b18dd1894c9217c299826dda5fb" \
# --data-binary @heykakao.wav