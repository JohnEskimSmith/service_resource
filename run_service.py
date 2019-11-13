# -*- coding: utf8 -*-
__author__ = 'sai'

from aiohttp import web
from codecs import decode
from base64 import b64encode
from os.path import exists
from sys import exit
from random import choice


async def handle_file(request):

    def return_file_base64(query_uid):
        if exists(files[query_uid]):
            with open(files[query_uid], 'rb') as image_reader:
                encoded_image = b64encode(image_reader.read())
                return decode(encoded_image)
        else:
            print(f"{query_uid}: , file: {files[query_uid]} not found")

    data_base64 = None
    query_uid = request.match_info['uuid']
    if query_uid in files:
        if query_uid not in cache_files:
            print(f'read from disk: {files[query_uid]}...')
            data_base64 = return_file_base64(query_uid)
            cache_files[query_uid] = data_base64
        else:
            print(f'read from memory: {files[query_uid]}...')
            data_base64 = cache_files[query_uid]
    else:
        print(f"not found {query_uid}")
    if not data_base64:
        data_base64 = ''
    if len(cache_files) > count_in_cache:
        for _ in range(count_remove):
            cache_files.pop(choice(list(cache_files.keys())))
        print(f'remove {count_remove} random keys from memory...')
    return web.Response(text=data_base64)


async def _handle(request):
    text = "need UUID"
    return web.Response(text=text)


def return_uuids_files(file_with_paths):
    if exists(file_with_paths):
        with open(file_with_paths, 'r') as info:
            rows = [row.replace('\n', '').replace('\r', '') for row in info.readlines()]
            files = {}
            for row in filter(lambda z:len(z)>0, rows):
                if ':' in row:
                    uuid, name_file = row.split(":")
                    if uuid not in files:
                        files[uuid] = name_file
                    else:
                        print(f'errors: {uuid} already exists')
            if len(files) >0:
                return files


if __name__ == '__main__':

    file_with_paths = "data.txt"
    files = return_uuids_files(file_with_paths)
    if not files:
        exit(1)

    cache_files = {}
    count_in_cache = 1000
    count_remove = 10

    app = web.Application()
    app.add_routes([web.get('/objects/ico/{uuid}', handle_file),
                    web.get('/', _handle)])
    web.run_app(app, host="127.0.0.1", port=30000)