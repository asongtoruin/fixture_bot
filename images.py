import urllib
import urllib.request

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps


class TextDraw(ImageDraw.ImageDraw):
    def align_text(self, text, x0, y0, x1, y1, font_path, ha='centre', va='centre', **kwargs):
        draw_args = (
            'font', 'spacing', 'direction', 'features', 
            'language', 'stroke_width'
        )
        draw_dict = dict()
        for d in draw_args:
            if d in kwargs.keys():
                draw_dict[d] = kwargs[d]
                
        size = self.maximise_text_size(
            text=text, max_w=x1-x0, max_h=y1-y0, font=font_path
        )
        font = ImageFont.truetype(font=font_path, size=size)
        
        w, h = self.textsize(text, font=font, **draw_dict)
        
        if ha == 'left':
            x = x0
        elif ha == 'right':
            x = x1 - w
        elif ha == 'centre':
            x = (x0 + x1 - w) / 2
        else:
            print(h, 'OH NO')
        
        if va == 'top':
            y = y0
        elif va == 'bottom':
            y = y1 - h
        elif va == 'centre':
            y = (y0 + y1 - h) / 2
        else:
            print(v, 'OH NO')
        
        self.text(xy=(x, y), text=text, font=font, **kwargs)
        
        # DEBUG - draw rectangle used by text
        # self.rectangle(xy=[x, y, x+w, y+h])
        
    def maximise_text_size(self, text, max_w, max_h, **kwargs):
        def fits(size):
            local_dict = {k: v for k, v in kwargs.items()}
            font = ImageFont.truetype(local_dict.pop('font'), size=size)
            w, h = self.textsize(text, font=font, **local_dict)
            
            return w <= max_w and h <= max_h
        
        upper = max_h
        while fits(upper):
            upper *= 2
        
        lower = int(upper / 2)
        while not fits(lower):
            lower = int(lower / 2)
        
        while (upper - lower) > 1:
            mid = int((upper + lower) / 2)
            if fits(mid):
                lower = mid
            else:
                upper = mid
                
        return lower
    
    
def scale_from_url(url, x0, y0, x1, y1, blur_size=3):
    w = x1 - x0
    h = y1 - y0

    img = Image.open(urllib.request.urlopen(url)).convert('RGBA')
    
    if blur_size:
        img = ImageOps.expand(img, border=blur_size*10, fill=(0,0,0,0))
        blur = img.filter(ImageFilter.GaussianBlur(radius=blur_size))
        blur.paste(img, mask=img)
        img = blur
    
    img = img.crop(img.getbbox())
    
    img_w, img_h = img.size

    if img_w >= img_h:
        new_w = w
        new_h = int(img_h * new_w / img_w)
    else:
        new_h = h
        new_w = int(img_w * new_h / img_h)

    scaled = img.resize((new_w, new_h), resample=Image.ANTIALIAS)

    new_x0 = x0 + int((w-new_w)/2)
    new_y0 = y0 +int((h-new_h)/2)

    return scaled, new_x0, new_y0
