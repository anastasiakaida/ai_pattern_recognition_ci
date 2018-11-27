class Item:

    def __init__(self, name, img, des, kp, id = None):
        self.name = name
        self.img = img
        self.des = des
        self.kp = kp
        self.id = id

    def get_img(self):
        return self.img.get_img()

    def get_img_grey(self):
        return self.img.get_img_grey()
