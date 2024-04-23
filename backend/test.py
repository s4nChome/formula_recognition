from recognize import Pix2Tex_recognize
from PIL import Image

img = Image.open('/home/s4nchome/文档/Code/uploads/0c74f549-65a8-427a-a070-ced0f3cdd4e3.png')
res,elapse = Pix2Tex_recognize(img)
print(res,elapse)