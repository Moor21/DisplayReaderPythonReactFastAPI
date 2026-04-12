import cv2
from ImageProcessing import ImageProcessing
from DigitBoxes import DigitBoxes
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
        self.minThresh = 80
        self.maxThresh = 100
        self.blur_kernel = (5,5)
        self.morph_kernel = (7,7)
        self.xFactor = 0.07
        self.yFactor = 0.25
        self.whole_digit = None

    def parameters_changing(self, parameters):
        print("Parameters: ", parameters)
        print("Old_parameters: ", self.minThresh, " ", self.maxThresh, " ", self.blur_kernel, " ", self.morph_kernel, " ", self.xFactor, " ", self.yFactor)
        self.minThresh = parameters.minThresh
        self.maxThresh = parameters.maxThresh
        if parameters.blur_kernel != 0:
            self.blur_kernel = (parameters.blur_kernel, parameters.blur_kernel)
        if parameters.morph_kernel != 0:
            self.morph_kernel =(parameters.morph_kernel,parameters.morph_kernel)
        self.xFactor = parameters.xFactor
        self.yFactor = parameters.yFactor
        print("New_parameters: ", self.minThresh, " ", self.maxThresh, " ", self.blur_kernel, " ", self.morph_kernel, " ", self.xFactor, " ", self.yFactor)

    def displayReader(self, image):
        self.pure_image = image
        canny = self.proc.getCannyImage(image, self.morph_kernel,self.minThresh,self.maxThresh,self.morph_kernel)
        self.canny_image = canny
        contours=self.proc.getContours(canny)
        img_contours = self.proc.getContoursImage(image,contours, (255,0,0));
        self.image_contours = img_contours
        marked_display = self.proc.findDisplayContour(image, contours)
        self.marked_display = marked_display
        if marked_display is not None:
            box = DigitBoxes(self.marked_display,self.proc)
            box.loadPureImage(self.marked_display, self.xFactor, self.yFactor)
            thresholdedDisplay = box.getDisplayThresholdImage()
            self.marked_display = thresholdedDisplay
            self.whole_digit = box.getWholeDigitString(thresholdedDisplay)

        
      
    def getPureImage(self):
        return self.pure_image
    def getCannyImage(self):
        return self.canny_image
    def getImageContours(self):
        return self.image_contours
    def getMarkedDisplayImage(self):
        return self.marked_display


