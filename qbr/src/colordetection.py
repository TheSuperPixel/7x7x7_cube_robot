#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et

import numpy as np
import cv2
from qbr.src.helpers import ciede2000, bgr2lab
from qbr.src.config import config
from qbr.src.constants import CUBE_PALETTE, COLOR_PLACEHOLDER

class ColorDetection:

    def __init__(self):
        self.prominent_color_palette = {
            'red'   : (0, 0, 255),#
            'orange': (0, 165, 255),
            'blue'  : (255, 0, 0),
            'green' : (0, 255, 0),
            'white' : (255, 255, 255),
            'yellow': (0, 255, 255)
        }
        # print("self.prominent_color_palette ="),print(self.prominent_color_palette)
        # Load colors from config and convert the list -> tuple.
        self.cube_color_palette = config.get_setting(
            CUBE_PALETTE,
            self.prominent_color_palette
        )
        # print("self.cube_color_palette ="),print(self.cube_color_palette)
        for side, bgr in self.cube_color_palette.items():
            self.cube_color_palette[side] = tuple(bgr)

    def get_prominent_color(self, bgr):
        """获取与给定bgr颜色等价的突出颜色."""
        for color_name, color_bgr in self.cube_color_palette.items():
            if tuple([int(c) for c in bgr]) == color_bgr:
                
                # color_trasnform={'red': 'R', 'orange': 'O', 'blue': 'B','green': 'G', 'white': 'W', 'yellow': 'Y'}
                # print(f"color_name={color_name}")
                return self.prominent_color_palette[color_name]
        return COLOR_PLACEHOLDER

    def get_dominant_color(self, roi):
        """
        从某个感兴趣的区域获得主色。

        :param roi:图像列表。
        返回:元组
        """
        pixels = np.float32(roi.reshape(-1, 3))

        n_colors = 1
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS
        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)
        dominant = palette[np.argmax(counts)]
        return tuple(dominant)

    def get_closest_color(self, bgr):
        """
        使用CIEDE2000距离获得最接近BGR颜色的颜色。

        :param bgr tuple:使用的bgr颜色。
        返回:dict类型
        """
        lab = bgr2lab(bgr)
        distances = []
        for color_name, color_bgr in self.cube_color_palette.items():
            distances.append({
                'color_name': color_name,
                'color_bgr': color_bgr,
                'distance': ciede2000(lab, bgr2lab(color_bgr))
            })
            # print("distances:"),print(type(distances)),print(distances)
        closest = min(distances, key=lambda item: item['distance'])
        # print("closest:"),print(type(closest)),print(closest)
        return closest

    def convert_bgr_to_notation(self, bgr):
        """
        Convert BGR tuple to rubik's cube notation.
        The BGR color must be normalized first by the get_closest_color method.

        :param bgr tuple: The BGR values to convert.
        :returns: str
        """
        notations = {
            'G' : 'F',
            'W' : 'U',
            'B'  : 'B',
            'R'   : 'R',
            'O': 'L',
            'Y': 'D'
        }
        color_name = self.get_closest_color(bgr)['color_name']
        return notations[color_name]

    def set_cube_color_pallete(self, palette):
        """
        Set a new cube color palette. The palette is being used when the user is
        scanning his cube in solve mode by matching the scanned colors against
        this palette.
        """
        for side, bgr in palette.items():
            self.cube_color_palette[side] = tuple([int(c) for c in bgr])

color_detector = ColorDetection()
