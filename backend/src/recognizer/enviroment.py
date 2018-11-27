import cv2

class Enviroment:

    def __init__(self, sensor):
        self.sensor = sensor
    
    def get_state(self):
        return self.sensor

    def save_state(self, img):
        cv2.imwrite('enviroment_state.jpg', img)

class CameraEnviroment(Enviroment):

    def get_state(self):
        buffer_size = self.sensor.get(cv2.CAP_PROP_BUFFERSIZE)
        while buffer_size >= 0:
            ret, frame = self.sensor.read()
            buffer_size -= 1
        return frame

    def get_state_grey(self):
        return cv2.cvtColor(self.get_state(), cv2.COLOR_BGR2GRAY)

class ImageEnviroment(Enviroment):

    def get_state(self):
        return self.sensor.get_img()

    def get_state_grey(self):
        return self.sensor.get_img_grey()
