import sys
import os

from fbragent import Agent
import enviroment
from item import Item
import image

import cv2

preview_img_path = os.path.abspath(os.path.dirname(sys.argv[0])) + '/../../img/book/dazai_2.JPG'

def main(env_type):
  
    if env_type == 'camera':
        c = cv2.VideoCapture(0)
        c.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        c.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        env = enviroment.CameraEnviroment(c)
    elif env_type == 'preview':
        env = enviroment.ImageEnviroment(image.ImagePath(preview_img_path))
    else:
        env = enviroment.ImageEnviroment(env_type)
    item_img_path = '../../img/book/dazai.JPG'
    item_img_path = '../../img/lord_of_the_flies/lotf_item.JPG'
    item_img = image.ImagePath(item_img_path)
    item = Item("Name", item_img, None, None)
    agent = Agent(env, item, True)

    while(True):
        agent.run()

if __name__ == "__main__":
    argv = sys.argv[1:]
    if len(argv) > 1:
        print("Usage: python3 main.py [type]")
        print("Types:")
        print(" camera - use attached camera")
        print(" preview - use hardcoded image")
        print(" <image path> - use image specified in path")
        sys.exit(1)
    
    t = 'camera' if len(argv) == 0 else argv[0]
    
    main(t)
