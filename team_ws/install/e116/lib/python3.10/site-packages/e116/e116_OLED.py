import time
import os
from smbus import SMBus
from PIL import Image,ImageDraw,ImageFont   
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from tf2_msgs.msg import TFMessage

address = 0x3c
bus = SMBus(7)

OLED_WIDTH   = 128 #OLED width
OLED_HEIGHT  = 32  #OLED height

font_lib= os.path.join(os.getcwd(), 'src/e116/e116/Font.ttc')
print(f"Current font_lib: {font_lib}")
font30 = ImageFont.truetype(font_lib, 30)

def delay_ms(delaytime):
    time.sleep(delaytime / 1000.0)
   
def i2c_writebyte(reg, value):
    bus.write_byte_data(address, reg, value)
    
def module_exit():
    bus.close()
    
class OLED_0in91(object):
    def __init__(self):
        self.width = OLED_WIDTH
        self.height = OLED_HEIGHT
        self.Column = OLED_WIDTH
        self.Page = int(OLED_HEIGHT//8)
        
    """    Write register address and data     """
    def command(self, cmd):
        i2c_writebyte(0x00, cmd)

    def data(self, data):
        i2c_writebyte(0x40, data)

    def Init(self):
        #self.reset()
        """Initialize display"""      
        #print("initialize register bgin")
        self.command(0xAE)

        self.command(0x40) # set low column address
        self.command(0xB0) # set high column address

        self.command(0xC8) # not offset

        self.command(0x81)
        self.command(0xff)

        self.command(0xa1)

        self.command(0xa6)

        self.command(0xa8)
        self.command(0x1f)

        self.command(0xd3)
        self.command(0x00)

        self.command(0xd5)
        self.command(0xf0)

        self.command(0xd9)
        self.command(0x22)

        self.command(0xda)
        self.command(0x02)

        self.command(0xdb)
        self.command(0x49)

        self.command(0x8d)
        self.command(0x14) 
        time.sleep(0.2)
        self.command(0xaf) #turn on OLED display 
        #print("initialize register over")
    
    def getbuffer(self, image):
        buf = [0xff] * (self.Page * self.Column)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        if(imwidth == self.width and imheight == self.height):
            #print ("Horizontal screen")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[x + int(y / 8) * self.width] &= ~(1 << (y % 8))
        elif(imwidth == self.height and imheight == self.width):
            #print ("Vertical screen")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[(newx + int(newy / 8 )*self.width) ] &= ~(1 << (y % 8))
        for x in range(self.Page * self.Column):
            buf[x] = ~buf[x]
        return buf 
            
    def ShowImage(self, pBuf):
        for i in range(0, self.Page):            
            self.command(0xB0 + i) # set page address
            self.command(0x00) # set low column address
            self.command(0x10) # set high column address
            # write data #
            for j in range(0, self.Column):
                self.data(pBuf[j+self.width*i])
                    
    def clear(self):
        """Clear contents of image buffer"""
        _buffer = [0x00]*(self.width * self.height//8)
        self.ShowImage(_buffer)
        
class E116OLED_Node(Node):
    def __init__(self):
        super().__init__('e116_OLED')
        qos = QoSProfile(depth=10)
        self.tag_num = -1
        self.disp = OLED_0in91()
        self.disp.Init()
        self.disp.clear()
        self.images = []
        for ii in range(20):
            self.images.append(Image.new('1', (self.disp.width, self.disp.height), "WHITE"))
            draw0 = ImageDraw.Draw(self.images[-1])
            draw0.text((31,0), str(ii), font = font30, fill = 0)
            self.images[-1]=self.images[-1].rotate(0)  #degree

        self.tags_sub = self.create_subscription(TFMessage, '/tf', self.callback, qos)
        self.tags_sub   # prevent unused variable warning
         

    def callback(self, data):
        if len(data.transforms) != self.tag_num:
            self.tag_num = len(data.transforms)
            self.disp.ShowImage(self.disp.getbuffer(self.images[self.tag_num]))
      
    
        
def main(args=None):
    rclpy.init(args=args)
    node = E116OLED_Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
    
