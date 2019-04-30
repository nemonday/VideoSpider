from PIL import Image
im=Image.open('1.jpg')
width=im.size[0]
height=im.size[1]

fh=open('1.txt','w')
for i in range(height):
    for j in range(width):
         #获取像素点颜色
         color=im.getpixel((j,i))
         colorsum=color[0]+color[1]+color[2]
         if(colorsum == 0):
            fh.write('1')
         else:
            fh.write('0')
            fh.write('\n')
         fh.close()