# -*- coding: utf-8 -*-
# Copyright (C) 2019 Vikas Chouhan
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import copy
import math
import random
import sys
from photocollage import collage, render

class UserCollage(object):
    """Represents a user-defined collage

    A UserCollage contains a list of photos (referenced by filenames) and a
    collage.Page object describing their layout in a final poster.

    """
    def __init__(self, photolist):
        self.photolist = photolist

    def make_page(self, opts):
        # Define the output image height / width ratio
        ratio = 1.0 * opts.out_h / opts.out_w

        # Compute a good number of columns. It depends on the ratio, the number
        # of images and the average ratio of these images. According to my
        # calculations, the number of column should be inversely proportional
        # to the square root of the output image ratio, and proportional to the
        # square root of the average input images ratio.
        avg_ratio = (sum(1.0 * photo.h / photo.w for photo in self.photolist) /
                     len(self.photolist))
        # Virtual number of images: since ~ 1 image over 3 is in a multi-cell
        # (i.e. takes two columns), it takes the space of 4 images.
        # So it's equivalent to 1/3 * 4 + 2/3 = 2 times the number of images.
        virtual_no_imgs = 2 * len(self.photolist)
        no_cols = int(round(math.sqrt(avg_ratio / ratio * virtual_no_imgs)))

        self.page = collage.Page(1.0, ratio, no_cols)
        random.shuffle(self.photolist)
        for photo in self.photolist:
            self.page.add_cell(photo)
        self.page.adjust()

class PhotoCollage(object):
    def __init__(self, image_list, border_w=0.01, border_c='black', out_w=800, out_r=1.0):
        assert len(image_list) > 0, 'Empty image list !!'

        super(PhotoCollage, self).__init__()
        self.history = []
        self.history_index = 0

        class Options(object):
            def __init__(self, border_w=0.01, border_c='black', out_w=800, out_h=600):
                self.border_w = border_w
                self.border_c = border_c
                self.out_w = out_w
                self.out_h = out_h
        self.opts = Options(border_w, border_c, out_w, int(out_w/out_r))

        self.photo_list = render.build_photolist(image_list)
        self.collage    = UserCollage(self.photo_list)
        self.collage.make_page(self.opts)

    def save_collage(self, savefile):
        collage = self.collage

        enlargement = float(self.opts.out_w) / collage.page.w
        collage.page.scale(enlargement)

        t = render.RenderingTask(
            collage.page, output_file=savefile,
            border_width=self.opts.border_w * max(collage.page.w,
                                                  collage.page.h),
            border_color=self.opts.border_c)
        t.start()
