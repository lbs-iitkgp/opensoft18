class coordinate:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class boundingBox:
    bound_text = ''
    box_type = ''
    tl = coordinate(0, 0)
    tr = coordinate(0, 0)
    br = coordinate(0, 0)
    bl = coordinate(0, 0)
    bb_children = []
    lexi_type = ''
    lexi_label = ''
    dosage = {}
    language = 'en'

    def __init__(self, tl, tr, bl, br, bound_text, box_type, bb_chilren):

        """
        :param tl: coordinates of top left
        :param tr: coordinates of top right
        :param bl: coordinates of bottom left
        :param br: coordinates of bottom right
        :param bound_text: The text inside the box
        :param box_type: categorize the box as line(L)/word(W)
        :param bb_children: List of all children objects of same type
        """

        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        self.bound_text = bound_text
        self.box_type = box_type
        self.bb_children = bb_chilren

        self.lexi_type = ''
        self.lexi_label = ''
        self.dosage = {}
        self.language = 'en'

    def __repr__(self):  # object definition
        return "<boundingBox box_type:%s bound_text:%s tl:(%s,%s) tr:(%s,%s) bl:(%s,%s) br:(%s,%s)>" % (self.box_type,
            self.bound_text, self.tl.x, self.tl.y, self.tr.x, self.tr.y, self.bl.x, self.bl.y, self.br.x, self.br.y)

    def __str__(self):  # print statement
        return "box_type:%s \nbound_text:%s \ntl:(%s,%s) \ntr:(%s,%s) \nbl:(%s,%s) \nbr:(%s,%s)" % (self.box_type,
            self.bound_text, self.tl.x, self.tl.y, self.tr.x, self.tr.y, self.bl.x, self.bl.y, self.br.x, self.br.y)
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class image_location:
    images_path = ''
    temp_path = ''
    image_name = ''
    image_id = ''

    def __init__(self, images_path, temp_path, image_name):
        self.images_path = images_path
        self.temp_path = temp_path
        self.image_name = image_name
        self.image_id = image_name.split('.')[-2]
