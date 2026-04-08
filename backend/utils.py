import cv2
from ImageProcessing import ImageProcessing
def get_image_bytes(img, image_type):
    frame_type = 1
    if image_type == 1:
        frame_type = 1
    elif image_type == 2:
        frame_type = 2
    elif image_type == 3:
        frame_type = 3
    elif image_type == 4:
        frame_type = 4
    ok, buffer = cv2.imencode(".jpg",img, [cv2.IMWRITE_JPEG_QUALITY,75])
    if ok:
        image_bytes = buffer.tobytes()
        packet = bytes([frame_type]) + image_bytes
        return packet
    else:
        return None


class DisplayReader:
    def __init__(self):    
        self.pure_image = None
        self.canny_image = None
        self.image_contours = None
        self.marked_display = None
        self.proc = ImageProcessing()

    def displayReader(self, image):
        self.pure_image = image
        canny = self.proc.getCannyImage(image, (5,5),80,100,(7,7))
        self.canny_image = canny
        contours=self.proc.getContours(canny)
        img_contours = self.proc.getContoursImage(image,contours, (255,0,0));
        self.image_contours = img_contours
        marked_display = self.proc.findDisplayContour(image, contours)
        if marked_display is not None:
            self.marked_display = marked_display
        
      
    def getPureImage(self):
        return self.pure_image
    def getCannyImage(self):
        return self.canny_image
    def getImageContours(self):
        return self.image_contours
    def getMarkedDisplayImage(self):
        return self.marked_display


