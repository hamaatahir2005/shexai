from pathlib import Path
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parent.parent
(root/'assets').mkdir(parents=True,exist_ok=True)
im=Image.new('RGBA',(256,256),'#080f1d');d=ImageDraw.Draw(im)
for r,w,c in [(104,5,'#163d5f'),(88,4,'#58dcf4'),(67,3,'#337caa')]:
    d.ellipse((128-r,128-r,128+r,128+r),outline=c,width=w)
d.polygon([(128,65),(168,143),(128,120),(88,143)],fill='#a8f3ff')
d.ellipse((117,157,139,179),fill='#58dcf4')
im.save(root/'assets/icon.ico',sizes=[(16,16),(32,32),(48,48),(128,128),(256,256)])
im.save(root/'assets/icon.png')
