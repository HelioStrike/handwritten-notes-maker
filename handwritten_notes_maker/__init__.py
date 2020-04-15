import numpy as np
from PIL import Image, ImageDraw, ImageFont
from threshold_image_maker import ThresholdImageMaker
import cv2
import random
import os
import io

page_dirs = ["left", "right"]
aligns = ["left", "center", "right"]

class HandwrittenNotesMaker():
    def __init__(self, left_margin, right_margin, top_margin, bottom_margin, font_path, papers_dir, line_space=50, page_dir="left", human_error=2):
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.font_path = font_path
        self.line_space = line_space

        assert page_dir in page_dirs, "Invalid value of page_dir."

        self.page_dir = page_dir
        self.papers_dir = papers_dir
        self.fonts = {}
        self.pages = []
        self.page_ptr = -1
        self.top_ptr = self.top_margin
        self.left_ptr = self.left_margin
        self.human_error = human_error
        self.draw = None
        self.to_next_page()

    def make_font(self, name, size, font_path=None):
        if font_path == None:
            font_path = self.font_path
        self.fonts[name] = ImageFont.truetype(font_path, size)

    def write_text(self, font_name, text):
        assert font_name in self.fonts.keys(), "font_name wasn't created yet."
        
        spaces = [i for i, c in enumerate(text) if c == ' '] + [len(text)]

        for index, letter in enumerate(text):
            if index == spaces[0]:
                spaces.pop(0)
            if((letter == "\n") or (self.left_ptr + self.draw.textsize(text[index:spaces[0]], self.fonts[font_name])[0] >= self.pages[self.page_ptr].size[0]-self.right_margin)):
                self.insert_new_line()
            if(self.top_ptr + self.draw.textsize(text[index:spaces[0]], self.fonts[font_name])[0] >= self.pages[self.page_ptr].size[1]-self.bottom_margin):
                self.to_next_page()
            human = random.randint(0,self.human_error)
            add_sub = random.randint(0,1)
            if(add_sub == 0):
                self.draw.text((self.left_ptr, self.top_ptr+human), letter, fill=(0,15,85,255), font=self.fonts[font_name])
            else:
                self.draw.text((self.left_ptr, self.top_ptr-human), letter, fill=(0,15,85,255), font=self.fonts[font_name])
            self.left_ptr += self.draw.textsize(letter, self.fonts[font_name])[0]


    def write_heading(self, font_name, text, align="center"):
        assert font_name in self.fonts.keys(), "font_name wasn't created yet."
        self.insert_new_line()
        assert align in aligns, "Invalid align value."
        if align == "center":
            self.left_ptr += (self.pages[self.page_ptr].width - self.left_margin - self.draw.textsize(text, self.fonts[font_name])[0])/2
        if align == "right":
            self.left_ptr = self.pages[self.page_ptr].width - self.left_margin - self.right_margin - self.draw.textsize(text, self.fonts[font_name])[0]
        self.write_text(font_name, text)
        self.insert_new_line()

    def insert_image(self, impath, dims=(300, 300)):
        assert dims is None or len(dims) == 2, "dims should be an tuple of size 2, or None."

        imaker = ThresholdImageMaker()
        img = imaker.make_binary_image(impath, threshold_mode='adaptive', clean_image=True)

        if dims is not None:
            img = cv2.resize(img, dims)

        self.insert_new_line()
        if self.top_ptr + len(img) > self.pages[self.page_ptr].height - self.bottom_margin:
            self.to_next_page()
        self.left_ptr = int((self.pages[self.page_ptr].width - self.left_margin - len(img[0]))/2)

        page = np.array(self.pages[self.page_ptr])
        page[list(np.array([[self.top_ptr],[self.left_ptr]]) + np.where(img == 0))] = [0,0,0]
        self.pages[self.page_ptr] = Image.fromarray(page, 'RGB')

        self.insert_new_line()
        

    def insert_vertical_space(self, space):
        self.left_ptr = self.left_margin
        self.top_ptr += space
        if self.top_ptr > self.pages[self.page_ptr].size[1] - self.bottom_margin:
            self.to_next_page()

    def insert_new_line(self):
        self.left_ptr = 0
        self.insert_vertical_space(self.line_space)

    def insert_new_page(self):
        dir_path = os.path.join(self.papers_dir, self.page_dir)
        if self.page_dir == page_dirs[0]:
            self.page_dir == page_dirs[1]
        else:
            self.page_dir == page_dirs[0]
        self.pages.append(Image.open(os.path.join(dir_path, random.choice(os.listdir(dir_path)))))

    def to_next_page(self):
        if self.page_ptr == len(self.pages)-1:
            self.insert_new_page()
        self.page_ptr += 1
        self.left_ptr = 0
        self.top_ptr = 0
        self.draw = ImageDraw.Draw(self.pages[self.page_ptr])

    def save_to_pdf(self, to_path):
        self.pages[0].save(to_path, "PDF" ,resolution=100.0, save_all=True, append_images=self.pages[1:])
