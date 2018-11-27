from flask import Flask, request, make_response, jsonify, Response, render_template

import cv2

from backend.src.server.db import Handler
from backend.src.server.json_encoder import AprJsonEncoder
import backend.src.server.converter as converter

from backend.src.recognizer.fbragent import Agent
from backend.src.recognizer.enviroment import CameraEnviroment
from backend.src.recognizer.item import Item
from backend.src.recognizer.image import ImageMongo

import threading
import time

app = Flask(__name__, template_folder='./frontend')
app.json_encoder = AprJsonEncoder
app.url_map.converters['ObjectId'] = converter.ObjectIdConverter
dbhandler = Handler()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
env = CameraEnviroment(cap)
agent = Agent(env, None, True)

state_img = None
item_cntr = None

@app.route('/')
def index():
    return '<img src="/stream" />'

# temporary method for item creation
@app.route('/create')
def create():
    return render_template('item_create.html')

@app.route('/stream')
def stream():
    def gen():
        global state_img
        while True:
            time.sleep(0.5)
            #img, cntr = agent.run()
            #retval, jpg = cv2.imencode('.jpg', img)
            retval, jpg = cv2.imencode('.jpg', state_img)
            resp = '--frame\r\n'.encode()
            resp += 'Content-Type: image/jpg\r\n\r\n'.encode()
            resp += jpg.tobytes()
            resp += '\r\n'.encode()
            yield resp
            
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/agent/recognize/image', methods = [ 'GET' ])
def recognizeImage():
    #img, cntr = agent.run()
    #retval, jpg = cv2.imencode('.jpg', img)
    global state_img
    retval, jpg = cv2.imencode('.jpg', state_img)
    response = make_response(jpg.tobytes())
    response.headers['Content-Type'] = 'image/jpg'
    return response

@app.route('/agent/recognize/coords', methods = [ 'GET' ])
def recognizeCoords():
    #img, cntr = agent.run()
    global item_cntr
    # TODO add timestamp
    if item_cntr is None:
        return jsonify({
            'x' : -1,
            'y' : -1
            })
    return jsonify({
            'x' : item_cntr.item(0),
            'y' : item_cntr.item(1)
            })

# id can be 00...00 to set item to None, which will stop recognition
@app.route('/agent/set_item/<ObjectId:id>', methods = [ 'GET' ])
def setItem(id):
    global dbhandler
    global agent
    try:
        item_data = dbhandler.find_item_one({ '_id' : id })
        item_image = dbhandler.find_image(item_data['img_id'])
        item = Item(
                item_data['name'],
                ImageMongo(item_image.read()),
                None,
                None,
                str(item_data['_id'])
                )
        agent.set_item(item)
    except:
        agent.set_item(None)

@app.route('/items', methods = [ 'GET' ] )
def getItems():
    global dbhandler
    items = dbhandler.find_item({})
    return jsonify(list(items))

@app.route('/items/<ObjectId:id>', methods = [ 'GET' ])
def getItem(id):
    global dbhandler
    item = dbhandler.find_item_one( { '_id' : id } )
    return jsonify(item)

@app.route('/items', methods = [ 'POST' ] )
def createItem():
    global dbhandler
    name = request.form['name']
    image = request.files['image'] 
    return jsonify(dbhandler.insert_item(name = name, image = image))

@app.route('/images/<ObjectId:id>', methods = [ 'GET' ])
def getImage(id):
    global dbhandler
    image = dbhandler.find_image(id)
    response = make_response(image.read())
    response.headers['Content-Type'] = image.content_type
    return response

def agent_loop():
    global agent
    global state_img
    global item_cntr
    while True:
        state_img, item_cntr = agent.run()

if __name__ == '__main__':
    t = threading.Thread(target=agent_loop)
    t.start()
    app.run(debug = True, use_reloader = False, host='0.0.0.0')
