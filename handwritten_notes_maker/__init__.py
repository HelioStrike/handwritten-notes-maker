import numpy as np
from PIL import Image, ImageDraw, ImageFont
from threshold_image_maker import ThresholdImageMaker
from .page_drawer import PageDrawer
import cv2
import random
import os
import io

page_dirs = ["left", "right"]
aligns = ["left", "center", "right"]

#Lets you create handwritten notes and save it to pdf

#line_space - space between 2 lines
#space_width - width of ' ' character
#text_color - color of ink printed on to the pdf
#page_dir - begin with left or right paper
#vertical_error - maximum value by which each character is offset
#spacing_error - space error between 2 characters
#character_rotation_error - each character is rotated by some value between these 2 numbers
#character_scale_x_min - each charaacter is scaled along x by atleast this value
#character_padding_x - each character is padded along x with this value
#character_padding_y - each character is padded along y with this value
class HandwrittenNotesMaker():
    def __init__(self, left_margin, right_margin, top_margin, bottom_margin, font_path, papers_dir, line_space=50, space_width=None, \
        text_color=(0,15,85,255), page_dir="left", vertical_error=0, spacing_error=0, character_rotation_error=(0,0), character_scale_x_min=0.8, \
        character_scale_y_min=0.8, character_padding_x=1, character_padding_y=2):
        
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.font_path = font_path
        self.line_space = line_space
        self.space_width = space_width

        self.set_page_dir(page_dir)
        self.set_text_color(text_color)
        
        self.papers_dir = papers_dir
        self.fonts = {}
        self.pages = []
        self.page_ptr = -1
        self.top_ptr = 0
        self.left_ptr = 0
        self.cur_width = None
        self.cur_height = None
        self.vertical_error = vertical_error
        self.spacing_error = spacing_error
        self.character_rotation_error = character_rotation_error
        self.character_scale_x_min = character_scale_x_min
        self.character_scale_y_min = character_scale_y_min
        self.character_padding_x = character_padding_x
        self.character_padding_y = character_padding_y
        self.draw = PageDrawer(fill=text_color, space_width=space_width, character_padding_x=character_padding_x, character_padding_y=character_padding_y)
        self.to_next_page()

    def set_page_dir(self, page_dir):
        assert page_dir in page_dirs, "Invalid value of page_dir."
        self.page_dir = page_dir

    def set_text_color(self, text_color):
        assert len(text_color) == 4, "Text color must be (red, green, blue, alpha)."
        self.text_color = text_color

    def set_vertical_error(self, vertical_error):
        self.vertical_error = vertical_error

    def set_spaciing_error(self, spacing_error):
        self.spacing_error = spacing_error

    def set_character_rotation_error(self, character_rotation_error):
        self.character_rotation_error = character_rotation_error

    def set_character_scale_x_min(self, character_scale_x_min):
        self.character_scale_x_min = character_scale_x_min

    def set_character_scale_y_min(self, character_scale_y_min):
        self.character_scale_y_min = character_scale_y_min

    def set_character_padding_x(self, character_padding_x):
        self.character_padding_x = character_padding_x

    def set_character_padding_y(self, character_padding_y):
        self.character_padding_y = character_padding_y

    #creates font of given size and style
    def make_font(self, name, size, font_path=None):
        if font_path == None:
            font_path = self.font_path
        self.fonts[name] = ImageFont.truetype(font_path, size)

    #writes text to the page using a declared style
    def write_text(self, font_name, text, space_width=None, vertical_error=None, spacing_error=None, new_line=False):
        assert font_name in self.fonts.keys(), "font_name wasn't created yet."
        
        if space_width is None:
            space_width = self.space_width
        if vertical_error is None:
            vertical_error = self.vertical_error
        if spacing_error is not None:
            spacing_error = self.spacing_error

        spaces = [i for i, c in enumerate(text) if c == ' '] + [len(text)]

        for index, letter in enumerate(text):
            if index == spaces[0]:
                spaces.pop(0)
            if((letter == "\n") or (self.left_margin + self.left_ptr + self.draw.textsize(text[index:spaces[0]], \
                self.fonts[font_name])[0] >= self.cur_width-self.right_margin)):
                self.insert_new_line()
            if(self.top_margin + self.top_ptr + self.draw.textsize(text[index:spaces[0]], self.fonts[font_name])[1] >= self.cur_height-self.bottom_margin):
                self.to_next_page()
            
            vertical_offset = random.randint(-self.vertical_error, self.vertical_error)
            spacing_offset = random.randint(-self.spacing_error, self.spacing_error)
            
            self.left_ptr += spacing_offset

            if space_width is not None and letter == ' ':
                self.left_ptr += space_width
            else:
                self.pages[self.page_ptr] = self.draw.text(self.pages[self.page_ptr], self.top_margin + self.top_ptr + vertical_offset, self.left_margin + self.left_ptr, \
                    letter, font=self.fonts[font_name], rotation=random.uniform(self.character_rotation_error[0],self.character_rotation_error[1]), \
                    scale_x=random.uniform(self.character_scale_x_min, 1), scale_y=random.uniform(self.character_scale_y_min, 1))
                self.left_ptr += self.draw.textsize(letter, self.fonts[font_name])[0]
        if new_line:
            self.insert_new_line()

    #writes text on a new line, and then adds a new line
    def write_heading(self, font_name, text, align="center", new_line=False):
        assert font_name in self.fonts.keys(), "font_name wasn't created yet."
        self.insert_new_line()
        assert align in aligns, "Invalid align value."
        if align == "center":
            self.left_ptr += (self.cur_width - self.left_margin - self.draw.textsize(text, self.fonts[font_name])[0])/2
        if align == "right":
            self.left_ptr = self.cur_width - self.left_margin - self.right_margin - self.draw.textsize(text, self.fonts[font_name])[0] - self.space_width*len(text.split(' '))
        self.write_text(font_name, text)
        if new_line:
            self.insert_new_line()

    #inserts image, center aligns it, padding it with 2 new lines
    def insert_image(self, impath, dims=(300, 300), new_line=False):
        assert dims is None or len(dims) == 2, "dims should be an tuple of size 2, or None."

        imaker = ThresholdImageMaker()
        img = imaker.make_binary_image(impath, threshold_mode='adaptive', clean_image=True)

        if dims is not None:
            img = cv2.resize(img, dims)

        self.insert_new_line()
        if self.top_ptr + len(img) > self.cur_height - self.bottom_margin:
            self.to_next_page()
        self.left_ptr = int((self.cur_width - self.left_margin - len(img[0]))/2)

        self.pages[self.page_ptr] = self.draw.image(self.pages[self.page_ptr], self.top_ptr, self.left_ptr, img, searchColor=0)
        self.top_ptr += len(img)
        if new_line:
            self.insert_new_line()
        
    #self-explanatory
    def insert_vertical_space(self, space):
        self.left_ptr = 0
        self.top_ptr += space
        if self.top_ptr > self.cur_height - self.bottom_margin:
            self.to_next_page()

    #inserts vertical space of size line_space
    def insert_new_line(self):
        self.left_ptr = 0
        self.insert_vertical_space(self.line_space)

    #inserts new page at the end
    def insert_new_page(self):
        dir_path = os.path.join(self.papers_dir, self.page_dir)
        if self.page_dir == page_dirs[0]:
            self.page_dir == page_dirs[1]
        else:
            self.page_dir == page_dirs[0]
        self.pages.append(np.array(Image.open(os.path.join(dir_path, random.choice(os.listdir(dir_path))))))

    #moves to next page, if there is no next page, a new page is created
    def to_next_page(self):
        if self.page_ptr == len(self.pages)-1:
            self.insert_new_page()
        self.cur_width = self.pages[self.page_ptr].shape[1]
        self.cur_height = self.pages[self.page_ptr].shape[0]
        self.page_ptr += 1
        self.left_ptr = 0
        self.top_ptr = 0

    #save pages to pdf
    def save_to_pdf(self, to_path):
        pages = list(map(lambda page: Image.fromarray(page, 'RGB'), self.pages))
        pages[0].save(to_path, "PDF" ,resolution=100.0, save_all=True, append_images=pages[1:])
