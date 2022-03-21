import os
import pickle
import requests
import pandas as pd
from init_photo_service import Create_Service


pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 150)
pd.set_option('display.max_colwidth', 150)
pd.set_option('display.width', 150)
pd.set_option('expand_frame_repr', True)

API_NAME = 'photoslibrary'
API_VERSION = 'v1'
CLIENT_SECRET_FILE = 'client_secret_calendar_api.json'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.sharing']
DISCOVERY_URL = 'https://www.googleapis.com/discovery/v1/apis/photoslibrary/v1/rest'
endpoint = 'mediasend_endpoint'

ul_service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, DISCOVERY_URL, endpoint, SCOPES)

token = pickle.load(open('token_photoslibrary_v1_mediasend_endpoint.pickle', 'rb'))
upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
send_tokens = []


def main(dest_album):
    album_id = get_album_id(dest_album)
    if album_id == 'Series([], )':
        create_album(dest_album)
        print('Created new Album')
        album_id = get_album_id(dest_album)
    upload_result = upload_album(album_id)
    print(upload_result)
    commit_result = commit_transfer(album_id)
    return


def create_album(album_name):
    request_body = {
        'album': {'title': album_name}
    }
    album_create_status = ul_service.albums().create(body=request_body).execute()
    return album_create_status


def get_album_id(source_album):
    try:
        response_albums = ul_service.albums().list(
            pageSize=50,
            excludeNonAppCreatedData=False
        ).execute()
        albums = response_albums.get('albums')
        next_page_token = response_albums.get('nextPageToken')
        while next_page_token:
            response_albums = ul_service.albums().list(
                pageSize=50,
                excludeNonAppCreatedData=False,
                pageToken=next_page_token
            ).execute()
            if response_albums.get('albums') is not None:
                albums.extend(response_albums.get('albums'))
            next_page_token = response_albums.get('nextPageToken')
        df_albums = pd.DataFrame(albums,
                                 columns=['id', 'title', 'productURL', 'mediaItemsCount', 'coverPhotoBaseURL',
                                          'coverMediaID'])
        print(df_albums['title'])
        ret_album_id = df_albums[df_albums['title'] == source_album]['id'].to_string(index=False).strip()
        return ret_album_id
    except Exception as e:
        print('Unable to find Album in get_album_id')
        print(e)
    return ()


def upload_album(ul_album_id):
    source_folder = r'.\CacheFolder'
    media_files = os.listdir(source_folder)
    send_files_count = len(media_files)
    if len(media_files) > 50:
        return 'GoogleAPIs limit upload batch sizes of 50 images or less'
    stop_count = 0
    for media_file in media_files:
        img_obj = os.path.join(source_folder, media_file)
        token_response = upload_image(img_obj, os.path.basename(img_obj), token, send_files_count)
        send_tokens.append(token_response.content.decode('utf-8'))
        send_files_count -= 1
        stop_count += 1
        if stop_count == 60:
            break
    return None


def upload_image(img_folder, img_name, ul_token, send_files_count):
    headers = {
        'Authorization': 'Bearer ' + ul_token.token,
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-Protocol': 'raw',
        'X-Goog-File-Name': img_name
    }
    img = open(img_folder, 'rb').read()
    response = requests.post(upload_url, data=img, headers=headers)
    print(send_files_count, ' - Uploading file ', img_name)
    return response


def commit_transfer(commit_album_id):
    new_media_items = [{'simpleMediaItem': {'uploadToken': each_token}} for each_token in send_tokens]
    request_body = {
        "albumId": commit_album_id,
        "newMediaItems": new_media_items
    }
    upload_response = ul_service.mediaItems().batchCreate(body=request_body).execute()
    return upload_response


if __name__ == "__main__":
    main('Cal project')
