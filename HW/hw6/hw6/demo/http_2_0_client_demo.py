import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from my import http_2_0_client
import json
import os
import glob
import threading
import xml.etree.ElementTree as ET

def write_file_from_response(file_path, response):
    if response:
        print(f"{file_path} begin")
        with open(file_path, "wb") as f:
            while True:
                content = response.get_stream_content()
                if content is None:
                    break
                f.write(content)
        print(f"{file_path} end")
    else:
        print("no response")
        
if __name__ == '__main__':
    client = http_2_0_client.HTTPClient()

    target_path = "../../target"
    response = client.get(url=f"127.0.0.1:8080/")
    file_list = []
    if response:
        headers = response.get_headers()
        if headers['content-type'] == 'text/html':
            body = response.get_full_body()
            root = ET.fromstring(body.decode())
            links = root.findall('.//a')
            file_list = []
            for link in links:
                file_list.append(link.text)

    for file in glob.glob(os.path.join(target_path, '*.txt')):
        os.remove(file)

    th_list = []
    for file in file_list:
        response = client.get(f"127.0.0.1:8080/static/{file}")
        th = threading.Thread(target=write_file_from_response, args=[f"{target_path}/{file}", response])
        th_list.append(th)
        th.start()
    # response = client.get(f"127.0.0.1:8080/static/{file_list[0]}")
    # th = threading.Thread(target=write_file_from_response, args=[f"{target_path}/{file_list[0]}", response])
    # th_list.append(th)
    # th.start()
        
    for th in th_list:
        th.join()