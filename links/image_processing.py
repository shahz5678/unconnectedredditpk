# coding=utf-8

# import arabic_reshaper
# from bidi.algorithm import get_display
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageFont, ImageDraw, ImageFile, ImageEnhance, ExifTags
ImageFile.LOAD_TRUNCATED_IMAGES = True
from redis1 import already_exists
# from page_controls import PERSONAL_GROUP_IMG_WIDTH

def enhance_image(image):
    enhancer = ImageEnhance.Brightness(image)
    enhancer = enhancer.enhance(1.06)
    enhancer2 = ImageEnhance.Contrast(enhancer)
    enhancer2 = enhancer2.enhance(1.02)
    enhancer3 = ImageEnhance.Color(enhancer2)
    return enhancer3.enhance(1.10)

def compute_avg_hash(image):
    small_image_bw = image.resize((8,8), Image.ANTIALIAS).convert("L")
    pixels = list(small_image_bw.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join(map(lambda pixel: '1' if pixel > avg else '0', pixels)) #turning the image into string of 0s and 1s
    photo_hash = int(bits, 2).__format__('16x').upper()
    return photo_hash

def restyle_image(image):
    # width = 400
    width = 300
    wpercent = (width/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image_resized = image.resize((width,hsize), Image.ANTIALIAS)
    return image_resized

def reorient_image(im):
    try:
        image_exif = im._getexif()
        image_orientation = image_exif[274]
        if image_orientation in (2,'2'):
            return im.transpose(Image.FLIP_LEFT_RIGHT)
        elif image_orientation in (3,'3'):
            return im.transpose(Image.ROTATE_180)
        elif image_orientation in (4,'4'):
            return im.transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (5,'5'):
            return im.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (6,'6'):
            return im.transpose(Image.ROTATE_270)
        elif image_orientation in (7,'7'):
            return im.transpose(Image.ROTATE_270).transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (8,'8'):
            return im.transpose(Image.ROTATE_90)
        else:
            return im
    except (KeyError, AttributeError, TypeError, IndexError):
        return im

def make_thumbnail(filee,quality,caption=None,already_resized=None):
    img = filee
    if img.mode != 'RGB':
        img = img.convert("RGB")
    img = enhance_image(img)
    #############
    if not already_resized:
        # JS users' images are resized in JS to 400x400. Non-JS users get to 300x300 below
        img.thumbnail((300, 300),Image.ANTIALIAS)
    # fillcolor = (255,255,255)#(255,0,0)red#(0,100,0)green#(0,0,0)black#(0,0,255)blue
    # shadowcolor = (0,0,0)
    # text = caption
    # draw_text(img,text,fillcolor,shadowcolor)
    #############
    thumbnailString = StringIO.StringIO()
    if quality:
        img.save(thumbnailString, 'JPEG', optimize=True,quality=80)
    else:
        img.save(thumbnailString, 'JPEG', optimize=True,quality=40)
    newFile = InMemoryUploadedFile(thumbnailString, None, 'temp.jpg', 'image/jpeg', thumbnailString.len, None)
    return newFile


# def prep_image(img,quality,max_width=None, already_resized=None):
#     if img.mode != 'RGB':
#         img = img.convert("RGB")
#     if already_resized:
#         img_width, img_height = img.size
#     else:
#         img, img_width, img_height = resize_image(img,max_width=max_width)
#     img = enhance_image(img)
#     thumbnailString = StringIO.StringIO()
#     if quality:
#         img.save(thumbnailString, 'JPEG', optimize=True,quality=60)
#     else:
#         img.save(thumbnailString, 'JPEG', optimize=True,quality=15)
#     # img.save(thumbnailString, 'JPEG', optimize=False,quality=100)
#     newFile = InMemoryUploadedFile(thumbnailString, None, 'temp.jpg', 'image/jpeg', thumbnailString.len, None)
#     return newFile, img_width, img_height


# used in PhotoReplyView (unreleased), PicsChatUploadView, PublicGroupView, PrivateGroupView, AdImageView (unreleased)
def clean_image_file(image,quality=None,already_reoriented=None, already_resized=None):
    if image:
        image = Image.open(image)
        # if float(image.height)/image.width > 7.0:
        #     return False
        if not already_reoriented:
            image = reorient_image(image)
        return make_thumbnail(filee=image,quality=quality,already_resized=already_resized)
    else:
        return 0

# # used by post_image_in_personal_group in group_views
# def process_personal_group_image(image, quality=None, already_resized=None, already_reoriented=None):
#     image = Image.open(image)
#     if float(image.height)/image.width > 7.0:
#         return None, 'too_high', 'too_high'
#     if not already_reoriented:
#         image = reorient_image(image) #so that it appears the right side up
#     return prep_image(image,quality,max_width=PERSONAL_GROUP_IMG_WIDTH,already_resized=already_resized)

# used by upload_public_photo in views
def clean_image_file_with_hash(image,quality=None,categ=None, caption=None, already_resized=None, already_reoriented=None):
    if image:
        image = Image.open(image)
         # if float(image.height)/image.width > 7.0:
         #    return None, 'too_high', 'too_high'
        if not already_reoriented:
            image = reorient_image(image) #so that it appears the right side up
        avghash = compute_avg_hash(image) #to ensure a duplicate image hasn't been posted before
        exists = already_exists(avghash, categ)
        if exists:
            return image, avghash, exists
        else:
            image = make_thumbnail(filee=image,quality=quality,caption=caption, already_resized=already_resized)
            return image, avghash, None
    else:
        return (0,-1)

################### DRAW TEXT ON IMAGE ###################

def text_with_stroke(draw,width,height,line,font,fillcolor,shadowcolor):
    # reshaped_text = arabic_reshaper.reshape(line)
    # line = get_display(reshaped_text)
    draw.text((width-1, height), line, font=font, fill=shadowcolor)
    draw.text((width+1, height), line, font=font, fill=shadowcolor)
    draw.text((width, height-1), line, font=font, fill=shadowcolor)
    draw.text((width, height+1), line, font=font, fill=shadowcolor)
    draw.text((width, height), line, font=font, fill=fillcolor)

def draw_text(img, text, fillcolor, shadowcolor, position='bottom'):
    text = text.strip()
    base_width, base_height = img.size #The image's size in pixels, as 2-tuple (width,height)
    font_size = base_width/15
    if font_size < 13:
        print "bad result"
    font = ImageFont.truetype("/usr/share/fonts/truetype/fonts-jameel/JameelNooriNastaleeq.ttf", font_size)
    ################Converting single-line text into multiple lines#################
    line = ""
    lines = []
    width_of_line = 0
    number_of_lines = 0
    for token in text.split():
        token = token+' '
        token_width = font.getsize(token)[0]
        if width_of_line+token_width < base_width:
            line+=token
            width_of_line+=token_width
        else:
            lines.append(line)
            number_of_lines += 1
            width_of_line = 0
            line = ""
            line+=token
            width_of_line+=token_width
    if line:
        lines.append(line)
        number_of_lines += 1
    #################################################################################
    draw = ImageDraw.Draw(img)#(background)
    if position == 'top':
        y = 2
        for line in lines:
            width, height = font.getsize(line)
            x = (base_width - width) / 2
            text_with_stroke(draw,x,y,line,font,fillcolor,shadowcolor)
            y += height
    elif position == 'middle':
        font_height = font.getsize('|')[1]
        text_height = font_height * number_of_lines
        y = (base_height-text_height)/2
        for line in lines:
            width, height = font.getsize(line)
            x = (base_width - width) / 2
            text_with_stroke(draw,x,y,line,font,fillcolor,shadowcolor)
            y += height
    else:
        font_height = font.getsize('|')[1]
        # background = Image.new('RGBA', (base_width, font_height*number_of_lines),(0,0,0,146)) #creating the black strip
        y = base_height-(font_height+3)#0
        for line in reversed(lines):
            width, height = font.getsize(line)
            x = (base_width - width) / 2
            text_with_stroke(draw,x,y,line,font,fillcolor,shadowcolor)
            y -= (height+2)
        # offset = (0,base_height/2) #get from user input (e.g. 'top', 'bottom', 'middle')
        # img.paste(background,offset,mask=background)