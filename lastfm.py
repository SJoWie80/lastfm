import requests, os, json, html
import sys
from PIL import Image, ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import datetime
from PIL import ImageFont


#last FM api settings
username = '' 
apikey = '' 


options = RGBMatrixOptions()
options.rows = 32
options.cols = 32
options.brightness = 50
options.chain_length = 2
options.parallel = 2
options.gpio_slowdown = 4
options.hardware_mapping = 'regular'
options.daemon = 1
matrix = RGBMatrix(options = options)


font_small = graphics.Font()
font_small.LoadFont("/home/pi/lastfm/tom-thumb.bdf")


white = graphics.Color(255, 255, 255)   
black = graphics.Color(0, 0, 0)
error = graphics.Color(0, 125, 0)

def get_current_track():

    f = "https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=" + username + "&api_key=" + apikey + "&format=json&limit=1" 
    try:
        request = requests.get(f)
    except:
        sys.exit(1)

    j = request.json()
    if 'recenttracks' in j:
        song = j['recenttracks']['track'][0]
        song_name = html.escape(song['name'])
        artist_name = html.escape(song['artist']['#text'])
        album_name = html.escape(song['album']['#text'])
        image_url = song['image'][-1]['#text']

        current_track_info = {
             "name":song_name,
             "image":image_url,
             "album":album_name,
             "artist":artist_name,

        }
    else:
        current_track_info = {
             "name":"error",
             "image":"https://st4.depositphotos.com/20524830/26158/i/600/depositphotos_261585304-stock-photo-abstract-unfocused-red-error-message.jpg",
             "album":"error",
             "artist":"ERROR! BRB",

        }


    return current_track_info

def clock():
    image = Image.new("RGB", (20, 5))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,31,31),fill=(0,0,0))
    matrix.SetImage(image, 44, 2)

    now = datetime.datetime.now()
    time_string = now.strftime('%H:%M')
    graphics.DrawText(matrix, font_small, 44, 7, white, time_string)

def main():
    current_track_id = None
    while True:
        current_track_info = get_current_track()
        clock()
        if current_track_info['name'] != current_track_id:

            image = requests.get(current_track_info['image'], stream=True)
            image.raw.decode_content = True
            with open(os.path.expanduser('/home/pi/lastfm/album_cover.jpg'), 'wb') as f:
                for chunk in image:
                    f.write(chunk)

            filesize = os.path.getsize("/home/pi/lastfm/album_cover.jpg")

            if filesize < 5000:
                image = Image.open('/home/pi/lastfm/noart.png')
                image.thumbnail((64,64), Image.ANTIALIAS)
                matrix.SetImage(image.convert('RGB'))


                graphics.DrawText(matrix, font_small, 8, 45, error, "No Artwork")  

            else:
                image = Image.open('/home/pi/lastfm/album_cover.jpg')
                image.thumbnail((64,64), Image.ANTIALIAS)
                matrix.SetImage(image.convert('RGB'))




            word = current_track_info['artist']
            number = (len(word)) * 4 

            image = Image.new("RGB", (number, 7))
            draw = ImageDraw.Draw(image)
            draw.rectangle((0,0,31,31),fill=(0,0,0))
            matrix.SetImage(image, 0, 55)


            graphics.DrawText(matrix, font_small, 1, 61, white, current_track_info['artist'])  

            clock()


        current_track_id = current_track_info['name']
        time.sleep(1)


if __name__ == '__main__':
    main()
