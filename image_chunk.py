import os
import glob
import PIL
from PIL import Image
import PIL.Image
from typing import Union
import time
import cv2
import numpy as np
import PIL.ImageChops


def split_image(image: PIL.Image, chunk_size: Union[int, tuple]) -> list:
    '''
    Split image into chunks.

    Parameters:
    - image: PIL Image object
    - chunk_size: int or tuple, size of chunks
        - if int, chunk shape is (chunk_size, chunk_size)
        - if tuple, chunk shape is (chunk_size[0], chunk_size[1])
        
    Returns: list of dictionaries like:
    ```
    {
        'resolution': image resolution,
        'chunk_id': chunk_id,
        'image_patch': image_patch
    }
    ```
    '''
    width, height = image.size
    resolution = (width, height)
    chunks = []
    chunk_id = 0

    if isinstance(chunk_size, int):
        chunk_size = (chunk_size, chunk_size)

    # crop image chunks
    for y in range(0, height, chunk_size[1]):
        for x in range(0, width, chunk_size[0]):
            image_patch = image.crop((x, y, x + chunk_size[0], y + chunk_size[1]))
            chunk_id += 1
            chunk = {
                'resolution': resolution,
                'chunk_id': chunk_id,
                'image_patch': image_patch
            }
            chunks.append(chunk)
    
    return chunks


def make_transfer_blob_list(image: PIL.Image, chunk_size: Union[int, tuple]) -> list:
    '''
    Make a list of transfer blobs of an image.

    Parameters:
    - image: PIL Image object
    - chunk_size: int or tuple, size of chunks
        - if int, chunk shape is (chunk_size, chunk_size)
        - if tuple, chunk shape is (chunk_size[0], chunk_size[1])
    
    Returns: a list of transfer blobs, each one is a dict like:
    ```
    {
        'timestamp': timestamp,
        'resolution': resolution,
        'total_chunk_cnt': total_chunk_cnt,
        'chunk_id': chunk_id,
        'image_path_encoded': image_path_encoded
    }
    ```
    '''
    chunks = split_image(image, chunk_size)
    total_chunk_cnt = len(chunks)
    transfer_blobs = []

    timestamp = time.time()

    for chunk in chunks:
        _, data = cv2.imencode('.jpg', np.array(chunk['image_patch']), [cv2.IMWRITE_JPEG_QUALITY, 50])

        transfer_blob = {
            'timestamp': timestamp,
            'resolution': chunk['resolution'],
            'total_chunk_cnt': total_chunk_cnt,
            'chunk_id': chunk['chunk_id'],
            'image_patch_encoded': data.tobytes()
        }
        # print(f'chunk_id: {chunk["id"]}, chunk_encoded len: {len(data.tobytes())}')
        transfer_blobs.append(transfer_blob)

    return transfer_blobs


def merge_chunks(transfer_blobs: list) -> PIL.Image:
    '''
    Merge chunks into a single image.

    Parameters:
    - transfer_blobs: list of transfer blobs, each one is a dict like:

    ```
    {
        'timestamp': timestamp,
        'resolution': resolution,
        'total_chunk_cnt': total_chunk_cnt,
        'chunk_id': chunk_id,
        'image_path_encoded': image_path_encoded
    }
    ```

    Returns: PIL Image object
    '''
    width, height = transfer_blobs[0]['resolution']
    image = PIL.Image.new('RGB', (width, height))
    
    for blob in transfer_blobs:
        i = blob['chunk_id']
        image_patch = cv2.imdecode(np.frombuffer(blob['image_patch_encoded'], np.uint8), cv2.IMREAD_COLOR)
        x = (i % (width // image_patch.shape[1])) * image_patch.shape[1]
        y = (i // (width // image_patch.shape[1])) * image_patch.shape[0]
        image.paste(PIL.Image.fromarray(cv2.cvtColor(image_patch, cv2.COLOR_BGR2RGB)), (x, y))

    return image


class ImagePool(object):
    '''
    Class of the image pool for the server, used to process the image chunk packs
    '''
    def __init__(self) -> None:
        '''
        Initialize an ImagePool object with two pools:
        - transfer_blob_pool: dict
        - reveiced_image_pool: list
        '''
        self.transfer_blob_pool = {}
        self.received_image_pool = []
    
    def add_transfer_blob(self, transfer_blob: dict) -> None:
        '''
        Add a transfer blob to the pool.

        Parameters:
        - transfer_blob: the received transfer blob to be added
        '''
        timestamp = transfer_blob['timestamp']

        if timestamp not in self.transfer_blob_pool:
            self.transfer_blob_pool[timestamp] = []
            timestamps = list(self.transfer_blob_pool.keys())
            if len(timestamps) > 1:
                timestamps.sort()
                for tmstp in timestamps[:-1]:
                    image = merge_chunks(self.transfer_blob_pool[tmstp])
                    self.received_image_pool.append({
                        'timestamp': tmstp,
                        'image': image
                    })
                    del self.transfer_blob_pool[tmstp]
        
        self.transfer_blob_pool[timestamp].append(transfer_blob)

        # if all chunk received, merge chunks into image
        if len(self.transfer_blob_pool[timestamp]) == transfer_blob['total_chunk_cnt']:
            image = merge_chunks(self.transfer_blob_pool[timestamp])
            self.received_image_pool.append({
                'timestamp': timestamp,
                'image': image
            })

            del self.transfer_blob_pool[timestamp]

            # remove all expired chunks in transfer_blob_pool
            for tmstp in list(self.transfer_blob_pool.keys()):
                if tmstp <= timestamp:
                    del self.transfer_blob_pool[tmstp]
    
    def has_new_image_received(self) -> bool:
        '''Check if there is a new image received.'''
        return bool(len(self.received_image_pool) > 0)
    
    def get_new_image(self) -> PIL.Image:
        '''Get the latest received image.'''
        return self.received_image_pool.pop(0)
    
