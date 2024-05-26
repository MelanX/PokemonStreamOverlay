import json
import os
import sys

from PIL import Image
from PIL.Image import Resampling, Transpose

WHITE = (255, 235, 255, 255)
BLACK = (0, 0, 0, 255)
TRANS = (0, 0, 0, 0)

TOP_LEFT_CORNER = [
    [None, None, BLACK, BLACK, None, None, None],
    [None, BLACK, WHITE, BLACK, BLACK, WHITE, BLACK],
    [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE],
    [BLACK, WHITE, WHITE, WHITE, WHITE, BLACK, WHITE],
    [None, BLACK, WHITE, WHITE, BLACK, WHITE, BLACK],
    [None, WHITE, BLACK, BLACK, WHITE, BLACK, None],
    [None, BLACK, WHITE, WHITE, BLACK, None, None]
]
TOP_RIGHT_CORNER = [
    [None, None, None, BLACK, BLACK, None, None],
    [BLACK, WHITE, BLACK, WHITE, BLACK, BLACK, None],
    [WHITE, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK],
    [WHITE, BLACK, WHITE, WHITE, WHITE, WHITE, BLACK],
    [BLACK, WHITE, BLACK, WHITE, WHITE, BLACK, None],
    [None, BLACK, WHITE, BLACK, BLACK, WHITE, None],
    [None, None, BLACK, WHITE, WHITE, BLACK, None]
]
BOTTOM_LEFT_CORNER = [
    [None, BLACK, WHITE, WHITE, BLACK, None, None],
    [None, WHITE, BLACK, BLACK, WHITE, BLACK, None],
    [None, BLACK, WHITE, BLACK, BLACK, WHITE, BLACK],
    [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, WHITE],
    [BLACK, WHITE, WHITE, WHITE, WHITE, BLACK, WHITE],
    [None, BLACK, WHITE, WHITE, BLACK, WHITE, BLACK],
    [None, None, BLACK, BLACK, None, None, None]
]
BOTTOM_RIGHT_CORNER = [
    [None, None, BLACK, WHITE, WHITE, BLACK, None],
    [None, BLACK, WHITE, BLACK, BLACK, BLACK, None],
    [BLACK, WHITE, BLACK, WHITE, BLACK, BLACK, None],
    [WHITE, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK],
    [WHITE, BLACK, WHITE, WHITE, WHITE, WHITE, BLACK],
    [BLACK, WHITE, BLACK, WHITE, WHITE, BLACK, None],
    [None, None, None, BLACK, BLACK, None, None]
]

LEFT_LINE = [BLACK, WHITE, BLACK, BLACK]
RIGHT_LINE = [BLACK, BLACK, WHITE, BLACK]
TOP_LINE = [BLACK, WHITE, BLACK, BLACK]
BOTTOM_LINE = [BLACK, WHITE, BLACK, BLACK]

with open("alphabet.json", "r") as f:
    ALPHABET = json.load(f)


def draw_frame(size, pixels, multiplier):
    # Function to set pixel values with multiplier
    def set_pixel_multiplied(px, x, y, color):
        if color is None:
            return
        for i in range(multiplier):
            for j in range(multiplier):
                px[x * multiplier + i, y * multiplier + j] = color

    # Corners
    for x in range(len(TOP_LEFT_CORNER)):
        for y in range(len(TOP_LEFT_CORNER[x])):
            set_pixel_multiplied(pixels, x, y, TOP_LEFT_CORNER[y][x])

    for x in range(len(TOP_RIGHT_CORNER)):
        for y in range(len(TOP_RIGHT_CORNER[x])):
            set_pixel_multiplied(pixels, size[0] // multiplier - len(TOP_RIGHT_CORNER) + x, y, TOP_RIGHT_CORNER[y][x])

    for x in range(len(BOTTOM_LEFT_CORNER)):
        for y in range(len(BOTTOM_LEFT_CORNER[x])):
            set_pixel_multiplied(pixels, x, size[1] // multiplier - len(BOTTOM_LEFT_CORNER) + y, BOTTOM_LEFT_CORNER[y][x])

    for x in range(len(BOTTOM_RIGHT_CORNER)):
        for y in range(len(BOTTOM_RIGHT_CORNER[x])):
            set_pixel_multiplied(pixels, size[0] // multiplier - len(BOTTOM_RIGHT_CORNER) + x, size[1] // multiplier - len(BOTTOM_RIGHT_CORNER) + y, BOTTOM_RIGHT_CORNER[y][x])

    # Lines
    for x in range(len(LEFT_LINE)):
        for y in range(len(TOP_LEFT_CORNER), size[1] // multiplier - len(BOTTOM_LEFT_CORNER[0])):
            set_pixel_multiplied(pixels, x + 1, y, LEFT_LINE[x])

    for x in range(len(RIGHT_LINE)):
        for y in range(len(TOP_RIGHT_CORNER), size[1] // multiplier - len(BOTTOM_RIGHT_CORNER[0])):
            set_pixel_multiplied(pixels, x + size[0] // multiplier - len(RIGHT_LINE) - 1, y, RIGHT_LINE[x])

    for x in range(len(TOP_LEFT_CORNER[0]), size[0] // multiplier - len(TOP_RIGHT_CORNER[0])):
        for y in range(len(TOP_LINE)):
            set_pixel_multiplied(pixels, x, y + 1, TOP_LINE[y])

    for x in range(len(BOTTOM_LEFT_CORNER[0]), size[0] // multiplier - len(BOTTOM_RIGHT_CORNER[0])):
        for y in range(len(BOTTOM_LINE)):
            set_pixel_multiplied(pixels, x, y + size[1] // multiplier - len(BOTTOM_LINE) - 1, BOTTOM_LINE[y])


def fill(pixels, original_size, size):
    x_offset = int((size[0] - original_size[0]) / 2)
    y_offset = int((size[1] - original_size[1]) / 2)
    for x in range(x_offset, size[0] - x_offset):
        for y in range(y_offset, size[1] - y_offset):
            pixels[x, y] = WHITE


def add_title(title, size, pixels, multiplier):
    def set_pixel_multiplied(px, x_start, x, y, color):
        if color is None:
            return
        for i in range(multiplier):
            for j in range(multiplier):
                px[x_start + (x * multiplier + i), y * multiplier + j] = color

    total_width = sum((len(get_char(c)[0]) * multiplier if c != ' ' else 4 * multiplier) + multiplier for c in title) - multiplier
    start_pos = (size[0] - total_width) // 2

    current_pos = start_pos
    for char in title:
        if char != " ":
            char_matrix = get_char(char)
            for x in range(len(char_matrix[0])):
                for y in range(len(char_matrix)):
                    set_pixel_multiplied(pixels, current_pos, x, y + len(char_matrix) + 1, char_matrix[y][x])
            current_pos += len(char_matrix[0]) * multiplier + multiplier
        else:
            current_pos += 4 * multiplier


def get_char(char: str):
    char = ALPHABET[char.upper()]
    return [[tuple(pixel) if pixel is not None else None for pixel in row] for row in char]


def load_pokedex_entry(id: int):
    file = f'pokedex/{id:03d}.png'
    if os.path.exists(file):
        return file

    if not os.path.exists('pokedex'):
        os.mkdir('pokedex')

    print(f'Trying to download pokedex entry {id}')
    import requests
    from bs4 import BeautifulSoup
    url = f'https://www.pokewiki.de/Datei:Hauptartwork_{id:03d}.png'
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    div = soup.find('div', class_='fullImageLink')
    if div:
        a_tag = div.find('a')
        if a_tag and 'href' in a_tag.attrs:
            img_url = 'https://www.pokewiki.de/' + a_tag['href']
            img_response = requests.get(img_url)
            img_response.raise_for_status()

            with open(file, 'wb') as f:
                f.write(img_response.content)

            print(f'Successfully downloaded {id}.png')
            return file
        else:
            print('No a tag or href attribute found')
    else:
        print('No div with class "fullImageLink" found')

    return None


def copy(base_img: Image, overlay, pos: tuple, rotation: int = 0, scale: float = 0, max_height: int = 0,
         max_width: int = 0, max_size: int = 0,
         flip: bool = False):
    temp_img = Image.new('RGBA', base_img.size, TRANS)
    if type(overlay) is str:
        overlay_img = Image.open(overlay)
    else:
        pokemon = load_pokedex_entry(overlay)
        if pokemon is None:
            return

        overlay_img = Image.open(pokemon)

    if rotation != 0:
        overlay_img = overlay_img.rotate(rotation, resample=Resampling.BICUBIC, expand=True)

    if scale != 0:
        overlay_img = overlay_img.resize((int(overlay_img.size[0] * scale), int(overlay_img.size[1] * scale)),
                                         Resampling.BOX)

    if max_size == 0:
        if max_height != 0 and max_width != 0:
            raise ValueError("Specify either max_height or max_width, not both.")
        elif max_height != 0:
            overlay_img = overlay_img.resize(
                (int((max_height / overlay_img.size[1]) * overlay_img.size[0]), max_height),
                Image.Resampling.BOX)
        elif max_width != 0:
            overlay_img = overlay_img.resize(
                (max_width, int((max_width / overlay_img.size[0]) * overlay_img.size[1])),
                Image.Resampling.BOX)
    else:
        # Assuming max_size is for the larger dimension
        width, height = overlay_img.size
        if width > height:
            overlay_img = overlay_img.resize(
                (max_size, int((max_size / width) * height)),
                Image.Resampling.BOX)
        else:
            overlay_img = overlay_img.resize(
                (int((max_size / height) * width), max_size),
                Image.Resampling.BOX)

    if flip:
        overlay_img = overlay_img.transpose(Transpose.FLIP_LEFT_RIGHT)

    temp_img.paste(overlay_img, pos)
    return Image.alpha_composite(base_img, temp_img)


def add_pkmn_slots(img: Image, pos: tuple):
    scale = 9
    for i in range(0, 6):
        img = copy(img, 'pokemon/slot.png', pos, scale=scale)
        pos = (pos[0] + 16 * scale, pos[1])

    return img


if __name__ == '__main__':
    if os.path.exists("config.json"):
        pkmn = None
        if len(sys.argv) > 1:
            pkmn = int(sys.argv[1])
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        img = Image.new('RGBA', (config['size'][0], config['size'][1]), TRANS)
        pixels = img.load()
        for panel in config['panels']:
            original_size = (panel['size'][0], panel['size'][1])
            multiplier = 4
            if 'multiplier' in panel:
                multiplier = int(panel['multiplier'])
            title = ""
            if 'title' in panel:
                title = panel['title']
            filled = True
            if 'filled' in panel:
                filled = panel['filled']

            size = (original_size[0] + (10 * multiplier), original_size[1] + (10 * multiplier))
            panelImg = Image.new('RGBA', size, TRANS)
            panelPx = panelImg.load()

            if filled:
                fill(panelPx, original_size, size)

            if title:
                add_title(panel['title'], size, panelPx, multiplier)

            draw_frame(size, panelPx, multiplier)
            img.paste(panelImg, (panel['pos'][0] - (5 * multiplier), panel['pos'][1] - (5 * multiplier)))

        logo = "pokemon/logo.png"
        if os.path.exists(logo):
            img = copy(img, logo, (-50, -80), rotation=15)
        else:
            print('If you want to have the Pokémon logo on your overlay, you need to download it (e.g. here: ' +
                  'https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/International_Pok%C3%A9mon_logo.svg/640px-International_Pok%C3%A9mon_logo.svg.png)\n' +
                  f'Save it here: {logo}')
        img = copy(img, pkmn if pkmn else 9, (-20, 800), max_height=300, flip=True)

        img = add_pkmn_slots(img, (275, 875))

        img.save('overlay.png')
    else:
        original_size = (int(input("x=")), int(input("y=")))
        image_name = f'frame{original_size[0]}x{original_size[1]}.png'
        multiplier = input("multiplier (default 4)=")
        multiplier = 4 if multiplier == "" else int(multiplier)
        size = (original_size[0] + (10 * multiplier), original_size[1] + (10 * multiplier))
        img = Image.new('RGBA', size, TRANS)
        pixels = img.load()
        if input("Fill? (y/N) ").lower() == "y":
            fill(pixels, original_size, size)

        title = input("Title: ")
        if title != "":
            add_title(title, size, pixels, multiplier)
            image_name = f'{title}.png'

        draw_frame(size, pixels, multiplier)
        img.save(image_name)
