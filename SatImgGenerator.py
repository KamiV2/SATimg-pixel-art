import requests
from PIL import Image
import io
import cv2
import os

TERMINAL_WIDTH = 140
BLOCK_PIXEL =  u"\u2584" #Unicode block for full pixel.

AR_SCALER = 0.3  #To counteract the aspect ratio of terminal characters
COLOR_SCALERS = [2, 2, 2]
COLOR_MIN = [0, 0, 0]
COLOR_MAX = [255, 255, 255]
ZOOM_LEVEL = 16

#Get location from IP address
def get_location():
    ip_parameters = {
        "token": "3eda20dcbf8200"
    }
    iprequest = requests.get('https://ipinfo.io',params=ip_parameters)
    country = iprequest.json()["city"] + ", " + iprequest.json()["country"]
    location = iprequest.json()["loc"]
    return location, country

#Returns RGB values post-filtering. Change constant COLOR_SCALERS, COLOR_MIN, COLOR_MAX to adjust parameters for filter,
def linear_image_color_filter(red, green, blue, scalers, min, max):
    rs = scalers[0]
    gs = scalers[1]
    bs = scalers[2]
    rmin = min[0]
    gmin = min[1]
    bmin = min[2]
    rmax = max[0]
    gmax = max[1]
    bmax = max[2]
    red *= rs
    green *= gs
    blue *= bs
    if red > rmax:
        red = rmax
    if green > gmax:
        green = gmax
    if blue > bmax:
        blue = bmax
    if red < rmin:
        red = rmin
    if green < gmin:
        green = gmin
    if blue < bmin:
        blue = bmin
    return int(red), int(green), int(blue)

#Retrieves map image
def generate_map(location,zoom, dim):
    dimstr = str(dim*10)
    map_parameters = {
        "apiKey":"-Bg4gLOVWSV0cC0ZUSi4swAktgiMXfpzgr7eRCErgsI",
        "c":location, #pulls latlong from location
        "h":dimstr, #image height
        "w":dimstr, #image width
        "t":"1", #terrain mode (sal)
        "z":zoom, #zoom level
        "nodot":"1", #hides dot in location
        "nocp":"1" #removes text
    }

    maprequest = requests.get('https://image.maps.ls.hereapi.com/mia/1.6/mapview', params = map_parameters)
    image_data = maprequest.content # byte values of the image
    image = Image.open(io.BytesIO(image_data))
    filename = "mappic.png"
    im1 = image.save(filename, format=None)
    return filename

#Returns unicode colored string containing 'text'
def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;5;255;255;255m".format(r, g, b, text)

#Main body of function
if __name__ == "__main__":
    #API call to ipinfo to retrieve location data from IP address
    location, country = get_location()
    #API call to HERE to retrieve map image
    fn = generate_map(location, ZOOM_LEVEL, TERMINAL_WIDTH)

    #Parses and scales the image
    img = cv2.imread(fn, cv2.IMREAD_COLOR)
    r = img.shape[0]
    c = img.shape[1]
    width = TERMINAL_WIDTH
    height = int(TERMINAL_WIDTH * r/c* (1-AR_SCALER))
    img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

    #Generates and prints string derived from pixel data of image
    prstr = ""
    for r in range(0, img.shape[0]):
        for c in range(0, img.shape[1]):
            red, grn, blu = img[r][c][2], img[r][c][1], img[r][c][0]
            red, grn, blu = linear_image_color_filter(red, grn, blu, COLOR_SCALERS, COLOR_MIN, COLOR_MAX)
            prstr += colored(red, grn, blu, BLOCK_PIXEL)
        prstr += "\n"

    print(prstr)
    datastr = colored(200, 200, 200, "Image Source: HERE API, Location: " +  country + " (" + location + ")")
    print(datastr)
    os.remove(fn)