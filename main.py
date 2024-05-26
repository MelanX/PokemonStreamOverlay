import json

from PIL import Image

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

    total_width = sum((len(get_char(c)[0]) * multiplier if c != ' ' else 4 * multiplier) for c in title)
    start_pos = (size[0] - total_width) // 2 - multiplier
    print(total_width)
    print(start_pos)

    i = 0
    current_pos = start_pos
    for char in title:
        i += 1

        if char != " ":
            char_matrix = get_char(char)
            for x in range(len(char_matrix[0])):
                for y in range(len(char_matrix)):
                    set_pixel_multiplied(pixels, current_pos, x, y + len(char_matrix) + 1, char_matrix[y][x])

            current_pos += (len(char_matrix[0]) + 1) * multiplier
        else:
            current_pos += 4 * multiplier

def get_char(char: str):
    char = ALPHABET[char.upper()]
    return [[tuple(pixel) if pixel is not None else None for pixel in row] for row in char]


if __name__ == '__main__':
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
