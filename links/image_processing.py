# coding=utf-8

from redis1 import already_exists
from PIL import Image, ImageFont, ImageDraw, ImageFile, ImageEnhance, ExifTags
ImageFile.LOAD_TRUNCATED_IMAGES = True
import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile



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

def reorient_image(image):
    try:
        image_exif = image._getexif()
        image_orientation = image_exif[274]
        if image_orientation == 3:
            image = image.transpose(Image.ROTATE_180)
        if image_orientation == 6:
            image = image.transpose(Image.ROTATE_270)
        if image_orientation == 8:
            image = image.transpose(Image.ROTATE_90)
        return image
    except:
        return image

def make_thumbnail(filee):
    img = filee
    # img = restyle_image(img) # only use this if you're not utilizing img.thumbnail()
    if img.mode != 'RGB':
        img = img.convert("RGB")
    enhancer = ImageEnhance.Brightness(img)
    enhancer = enhancer.enhance(1.10)
    enhancer2 = ImageEnhance.Contrast(enhancer)
    enhancer2 = enhancer2.enhance(1.04)
    enhancer3 = ImageEnhance.Color(enhancer2)
    img = enhancer3.enhance(1.15)
    #############
    img.thumbnail((300, 300),Image.ANTIALIAS)
    # fillcolor = (255,255,255)#(255,0,0)red#(0,100,0)green#(0,0,0)black#(0,0,255)blue
    # shadowcolor = (0,0,0)
    # text = u'مسجد' #urdu se angrezi
    # draw_text(img,text,fillcolor,shadowcolor)
    #############
    thumbnailString = StringIO.StringIO()
    img.save(thumbnailString, 'JPEG', optimize=True,quality=40)
    newFile = InMemoryUploadedFile(thumbnailString, None, 'temp.jpg', 'image/jpeg', thumbnailString.len, None)
    return newFile

# used in PhotoReplyView (unreleased), PicsChatUploadView, PublicGroupView, PrivateGroupView, AdImageView
def clean_image_file(image): # where self is the form
    if image:
        image = Image.open(image)
        image = reorient_image(image)
        image = make_thumbnail(image)
        #print "thumbnailed image is %s" % image.size
        return image
    else:
        return 0

# used by upload_public_photo in views
def clean_image_file_with_hash(image):#, hashes): # where self is the form
    if image:
        image = Image.open(image)
        image = reorient_image(image) #so that it appears the right side up
        avghash = compute_avg_hash(image) #to ensure a duplicate image hasn't been posted before
        exists = already_exists(avghash)
        if exists:
            return image, avghash, exists
        else:
            image = make_thumbnail(image)
            return image, avghash, None
    else:
        return (0,-1)

################### DRAW TEXT ON IMAGE ###################

def text_with_stroke(draw,width,height,line,font,fillcolor,shadowcolor):
    # print line
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
    # print font
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