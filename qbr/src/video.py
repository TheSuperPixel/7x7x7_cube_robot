#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et
import cv2
from qbr.src.colordetection import color_detector
from qbr.src.config import config
from qbr.src.helpers import get_next_locale
import i18n
from PIL import ImageFont, ImageDraw, Image
import numpy as np
from qbr.src.constants import (
    COLOR_PLACEHOLDER,
    LOCALES,
    ROOT_DIR,
    CUBE_PALETTE,
    MINI_STICKER_AREA_TILE_SIZE,
    MINI_STICKER_AREA_TILE_GAP,
    MINI_STICKER_AREA_OFFSET,
    STICKER_AREA_TILE_SIZE,
    STICKER_AREA_TILE_GAP,
    STICKER_AREA_OFFSET,
    MY_STICKER_AREA_OFFSET_X,
    MY_STICKER_AREA_OFFSET_Y,
    STICKER_CONTOUR_COLOR,
    CALIBRATE_MODE_KEY,
    SWITCH_LANGUAGE_KEY,
    TEXT_SIZE,
    E_INCORRECTLY_SCANNED,
    E_ALREADY_SOLVED
)

class Webcam:

    def __init__(self):
        # print('Starting webcam... (this might take a while, please be patient)')
        # self.cam = cv2.VideoCapture(0)
        # print('Webcam successfully started')

        self.colors_to_calibrate = ['green', 'red', 'blue', 'orange', 'white', 'yellow']
        self.average_sticker_colors = {}
        self.result_state = {}

        self.snapshot_state = [(255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255)]
        self.preview_state  = [(255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255),
                               (255,255,255), (255,255,255), (255,255,255),(255,255,255), (255,255,255), (255,255,255),(255,255,255)]

        # self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        # self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.calibrate_mode = False
        self.calibrated_colors = {}
        self.current_color_to_calibrate_index = 0
        self.done_calibrating = False

    def draw_stickers(self, preview,stickers, offset_x, offset_y):
        """Draws the given stickers onto the given frame."""
        index = -1
        for row in range(7):
            for col in range(7):
                index += 1
                x1 = (offset_x + STICKER_AREA_TILE_SIZE * col) + STICKER_AREA_TILE_GAP * col
                y1 = (offset_y + STICKER_AREA_TILE_SIZE * row) + STICKER_AREA_TILE_GAP * row
                x2 = x1 + STICKER_AREA_TILE_SIZE
                y2 = y1 + STICKER_AREA_TILE_SIZE

                # shadow
                cv2.rectangle(
                    preview,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 0),
                    -1
                )

                # foreground color
                cv2.rectangle(
                    preview,
                    (x1 + 1, y1 + 1),
                    (x2 - 1, y2 - 1),
                    color_detector.get_prominent_color(stickers[index]),
                    -1
                )

    def draw_preview_stickers(self,preview):
        """Draw the current preview state onto the given frame."""
        self.draw_stickers(preview,self.preview_state, MY_STICKER_AREA_OFFSET_X, MY_STICKER_AREA_OFFSET_Y)

    def draw_snapshot_stickers(self):
        """Draw the current snapshot state onto the given frame."""
        y = STICKER_AREA_TILE_SIZE * 3 + STICKER_AREA_TILE_GAP * 2 + STICKER_AREA_OFFSET * 2
        self.draw_stickers(self.snapshot_state, STICKER_AREA_OFFSET, y)

    def find_contours(self, dilatedFrame):
        """Find the contours of a 3x3x3 cube."""
        contours, hierarchy = cv2.findContours(dilatedFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        final_contours = []

        # Step 1/4: 将所有轮廓过滤为仅为方形的轮廓。
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.1 * perimeter, True)
            if len (approx) == 4:
                area = cv2.contourArea(contour)
                (x, y, w, h) = cv2.boundingRect(approx)

                # Find aspect ratio of boundary rectangle around the countours.
                ratio = w / float(h)

                # Check if contour is close to a square.
                if ratio >= 0.8 and ratio <= 1.2 and w >= 30 and w <= 60 and area / (w * h) > 0.4:
                    final_contours.append((x, y, w, h))

        # Return early if we didn't found 9 or more contours.
        if len(final_contours) < 9:
            return []

        # Step 2/4: Find the contour that has 9 neighbors (including itself)
        # and return all of those neighbors.
        found = False
        contour_neighbors = {}
        for index, contour in enumerate(final_contours):
            (x, y, w, h) = contour
            contour_neighbors[index] = []
            center_x = x + w / 2
            center_y = y + h / 2
            radius = 1.5

            # 为当前轮廓线创建9个位置
            # 邻居。我们将使用它来检查每个轮廓有多少邻居
            # 所有这些能匹配的唯一方法是如果当前的轮廓
            # 是立方体的中心。如果我们找到了中心，我们也知道
            # 所有的邻居，从而知道所有的轮廓，从而知道
            # 这个形状可以被认为是一个3x3x3的立方体。当我们找到这些的时候
            # contours，我们对它们排序并返回它们。
            neighbor_positions = [
                # top left
                [(center_x - w * radius), (center_y - h * radius)],

                # top middle
                [center_x, (center_y - h * radius)],

                # top right
                [(center_x + w * radius), (center_y - h * radius)],

                # middle left
                [(center_x - w * radius), center_y],

                # center
                [center_x, center_y],

                # middle right
                [(center_x + w * radius), center_y],

                # bottom left
                [(center_x - w * radius), (center_y + h * radius)],

                # bottom middle
                [center_x, (center_y + h * radius)],

                # bottom right
                [(center_x + w * radius), (center_y + h * radius)],
            ]

            for neighbor in final_contours:
                (x2, y2, w2, h2) = neighbor
                for (x3, y3) in neighbor_positions:
                    # The neighbor_positions are located in the center of each
                    # contour instead of top-left corner.
                    # logic: (top left < center pos) and (bottom right > center pos)
                    if (x2 < x3 and y2 < y3) and (x2 + w2 > x3 and y2 + h2 > y3):
                        contour_neighbors[index].append(neighbor)

        #步骤3/4:现在我们知道了所有轮廓有多少邻居，我们将
        #循环它们，找到有9个邻居的等高线
        #包括它自己。这是立方体的中心部分。如果我们来
        #横过它，那么“邻居”实际上是我们的所有轮廓
        #寻找。
        for (contour, neighbors) in contour_neighbors.items():
            if len(neighbors) == 9:
                found = True
                final_contours = neighbors
                break

        if not found:
            return []

        #步骤4/4:当我们到达这部分代码时，我们发现了一个立方体
        #轮廓。下面的代码将在其X和Y上对所有轮廓进行排序
        #从左上到右下。
        # Sort contours on the y-value first.
        y_sorted = sorted(final_contours, key=lambda item: item[1])

        # Split into 3 rows and sort each row on the x-value.
        top_row = sorted(y_sorted[0:3], key=lambda item: item[0])
        middle_row = sorted(y_sorted[3:6], key=lambda item: item[0])
        bottom_row = sorted(y_sorted[6:9], key=lambda item: item[0])

        sorted_contours = top_row + middle_row + bottom_row
        # print(type(sorted_contours))
        print(sorted_contours)
        return sorted_contours

    def scanned_successfully(self):
        """Validate if the user scanned 9 colors for each side."""
        color_count = {}
        for side, preview in self.result_state.items():
            for bgr in preview:
                key = str(bgr)
                if key not in color_count:
                    color_count[key] = 1
                else:
                    color_count[key] = color_count[key] + 1
        invalid_colors = [k for k, v in color_count.items() if v != 9]
        return len(invalid_colors) == 0

    def draw_contours(self, contours,preview):
        """Draw contours onto the given frame."""
        if self.calibrate_mode:
            # Only show the center piece contour.
            (x, y, w, h) = contours[24]
            cv2.rectangle(preview, (x, y), (x + w, y + h), STICKER_CONTOUR_COLOR, 2)
        else:
            for index, (x, y, w, h) in enumerate(contours):
                cv2.rectangle(preview,(x, y), (x + w, y + h), STICKER_CONTOUR_COLOR, 2)

    def update_preview_state(self, contours,preview):
        """
        获得每X帧的轮廓的平均颜色值
        防止闪烁和更精确的结果。
        """
        max_average_rounds = 8
        # print("contours"),print(type(contours)),print(contours)
        # print("enumerate(contours)"),print(type(enumerate(contours))),print(enumerate(contours))
        for index, (x, y, w, h) in enumerate(contours):
            # print("index:"),print(type(index)),print(index)
            #enumerate()函数适用于需要同时获取索引和元素值的情况，而直接对可迭代对象进行迭代则不需要使用enumerate()函数

            # if index in self.average_sticker_colors and len(self.average_sticker_colors[index]) == max_average_rounds:
            #     #如果self.average_sticker_colors的某个索引（色块）的存储数量大于max_average_rounds，那就会在这段函数里统计
            #     #出现近似颜色次数最多的近似颜色，用这个颜色作为self.preview_state字典对应色块颜色的新颜色 （重复识别提高准确度）
            #     sorted_items = {}
            #     for bgr in self.average_sticker_colors[index]:
            #         key = str(bgr)
            #         if key in sorted_items:
            #             sorted_items[key] += 1
            #         else:
            #             sorted_items[key] = 1
            #     # print("sorted_items"),print(type(sorted_items)),print(sorted_items)
            #     most_common_color = max(sorted_items, key=lambda i: sorted_items[i])#max()函数会返回sorted_items中值最大的元素。
            #     self.average_sticker_colors[index] = []
            #     self.preview_state[index] = eval(most_common_color)
            #     break

            roi = preview[y+7:y+h-7, x+14:x+w-14]
            # cv2.rectangle(self.frame, (x+14, y+7), (x+w-14, y+h-7), (0, 0, 255), 2)
            avg_bgr = color_detector.get_dominant_color(roi)#从某个感兴趣的区域获得主色
            # print("avg_bgr:"),print(type(avg_bgr)),print(avg_bgr)
            closest_color = color_detector.get_closest_color(avg_bgr)['color_bgr']#取得最近的颜色，从返回字典取索引得到颜色
            #color_detector.get_closest_color返回了字典，通过“['color_bgr']”取bgr部分得到元组
            # print("closest_color"),print(type(closest_color)),print(closest_color)
            self.preview_state[index] = closest_color
            # self.preview_state #存储着每个色块颜色识别近似后的颜色
            # print("self.preview_state:"),print(type(self.preview_state)),print(self.preview_state)
            if index in self.average_sticker_colors:
                self.average_sticker_colors[index].append(closest_color)
            else:
                self.average_sticker_colors[index] = [closest_color]
            #每个色块近似后的颜色会被存入self.average_sticker_colors字典中，
            #这个字典的每个索引会存放同一个色块经过多次是识别后的不同近似颜色结果
            # print('---------------------------------------------------')
            # print("self.average_sticker_colors")
            # print(type(self.average_sticker_colors))
            # print(self.average_sticker_colors)
            # print('---------------------------------------------------')

    def update_snapshot_state(self):
        """Update the snapshot state based on the current preview state."""
        self.snapshot_state = list(self.preview_state)
        center_color_name = color_detector.get_closest_color(self.snapshot_state[4])['color_name']
        self.result_state[center_color_name] = self.snapshot_state
        self.draw_snapshot_stickers()

    def get_font(self, size=TEXT_SIZE):
        """Load the truetype font with the specified text size."""
        font_path = '{}/assets/arial-unicode-ms.ttf'.format(ROOT_DIR)
        return ImageFont.truetype(font_path, size)

    def render_text(self, text, pos, color=(255, 255, 255), size=TEXT_SIZE, anchor='lt'):
        """
        Render text with a shadow using the pillow module.
        """
        font = self.get_font(size)

        # Convert opencv frame (np.array) to PIL Image array.
        frame = Image.fromarray(self.frame)

        # Draw the text onto the image.
        draw = ImageDraw.Draw(frame)
        draw.text(pos, text, font=font, fill=color, anchor=anchor,
                  stroke_width=1, stroke_fill=(0, 0, 0))

        # Convert the pillow frame back to a numpy array.
        self.frame = np.array(frame)

    def get_text_size(self, text, size=TEXT_SIZE):
        """Get text size based on the default freetype2 loaded font."""
        return self.get_font(size).getsize(text)

    def draw_scanned_sides(self):
        """Display how many sides are scanned by the user."""
        text = i18n.t('scannedSides', num=len(self.result_state.keys()))
        self.render_text(text, (20, self.height - 20), anchor='lb')

    def draw_current_color_to_calibrate(self):
        """显示需要校准的当前边的颜色。"""
        offset_y = 20
        font_size = int(TEXT_SIZE * 1.25)
        if self.done_calibrating:
            messages = [
                'calibratedSuccessfully',
                'quitCalibrateMode'
            ]
            for index, text in enumerate(messages):
                _, textsize_height = self.get_text_size(text, font_size)
                y = offset_y + (textsize_height + 10) * index
                print(text)
        else:
            current_color = self.colors_to_calibrate[self.current_color_to_calibrate_index]
            print(f"currentCalibratingSide.{format(current_color)}")
            

    def draw_calibrated_colors(self,preview):
        """Display all the colors that are calibrated while in calibrate mode."""
        offset_y = 20
        for index, (color_name, color_bgr) in enumerate(self.calibrated_colors.items()):
            x1 = 90
            y1 = int(offset_y + STICKER_AREA_TILE_SIZE * index)
            x2 = x1 + STICKER_AREA_TILE_SIZE
            y2 = y1 + STICKER_AREA_TILE_SIZE

            # shadow
            cv2.rectangle(
                preview,
                (x1, y1),
                (x2, y2),
                (0, 0, 0),
                -1
            )

            # foreground
            cv2.rectangle(
                preview,
                (x1 + 1, y1 + 1),
                (x2 - 1, y2 - 1),
                tuple([int(c) for c in color_bgr]),
                -1
            )
            print(f"color_name:{color_name}")
            # self.render_text(i18n.t(color_name), (20, y1 + STICKER_AREA_TILE_SIZE / 2 - 3), anchor='lm')

    def reset_calibrate_mode(self):
        """重置校准模式变量."""
        self.calibrated_colors = {}
        self.current_color_to_calibrate_index = 0
        self.done_calibrating = False

    def draw_current_language(self):
        text = '{}: {}'.format(
            i18n.t('language'),
            LOCALES[config.get_setting('locale')]
        )
        offset = 20
        self.render_text(text, (self.width - offset, offset), anchor='rt')

    def draw_2d_cube_state(self):
        """
        Create a 2D cube state visualization and draw the self.result_state.

        We're gonna display the visualization like so:
                    -----
                  | W W W |
                  | W W W |
                  | W W W |
            -----   -----   -----   -----
          | O O O | G G G | R R R | B B B |
          | O O O | G G G | R R R | B B B |
          | O O O | G G G | R R R | B B B |
            -----   -----   -----   -----
                  | Y Y Y |
                  | Y Y Y |
                  | Y Y Y |
                    -----
        So we're gonna make a 4x3 grid and hardcode where each side has to go.
        Based on the x and y in that 4x3 grid we can calculate its position.
        """
        grid = {
            'white' : [1, 0],
            'orange': [0, 1],
            'green' : [1, 1],
            'red'   : [2, 1],
            'blue'  : [3, 1],
            'yellow': [1, 2],
        }

        # The offset in-between each side (white, red, etc).
        side_offset = MINI_STICKER_AREA_TILE_GAP * 3

        # The size of 1 whole side (containing 9 stickers).
        side_size = MINI_STICKER_AREA_TILE_SIZE * 3 + MINI_STICKER_AREA_TILE_GAP * 2

        # The X and Y offset is placed in the bottom-right corner, minus the
        # whole size of the 4x3 grid, minus an additional offset.
        offset_x = self.width - (side_size * 4) - (side_offset * 3) - MINI_STICKER_AREA_OFFSET
        offset_y = self.height - (side_size * 3) - (side_offset * 2) - MINI_STICKER_AREA_OFFSET

        for side, (grid_x, grid_y) in grid.items():
            index = -1
            for row in range(3):
                for col in range(3):
                    index += 1
                    x1 = int(
                        (offset_x + MINI_STICKER_AREA_TILE_SIZE * col) +
                        (MINI_STICKER_AREA_TILE_GAP * col) +
                        ((side_size + side_offset) * grid_x)
                    )
                    y1 = int(
                        (offset_y + MINI_STICKER_AREA_TILE_SIZE * row) +
                        (MINI_STICKER_AREA_TILE_GAP * row) +
                        ((side_size + side_offset) * grid_y)
                    )
                    x2 = int(x1 + MINI_STICKER_AREA_TILE_SIZE)
                    y2 = int(y1 + MINI_STICKER_AREA_TILE_SIZE)

                    foreground_color = COLOR_PLACEHOLDER
                    if side in self.result_state:
                        foreground_color = color_detector.get_prominent_color(self.result_state[side][index])

                    # shadow
                    cv2.rectangle(
                        self.frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 0),
                        -1
                    )

                    # foreground color
                    cv2.rectangle(
                        self.frame,
                        (x1 + 1, y1 + 1),
                        (x2 - 1, y2 - 1),
                        foreground_color,
                        -1
                    )

    def get_result_notation(self):
        """Convert all the sides and their BGR colors to cube notation."""
        notation = dict(self.result_state)
        for side, preview in notation.items():
            for sticker_index, bgr in enumerate(preview):
                notation[side][sticker_index] = color_detector.convert_bgr_to_notation(bgr)

        # Join all the sides together into one single string.
        # Order must be URFDLB (white, red, green, yellow, orange, blue)
        combined = ''
        for side in ['white', 'red', 'green', 'yellow', 'orange', 'blue']:
            combined += ''.join(notation[side])
        return combined

    def state_already_solved(self):
        """Find out if the cube hasn't been solved already."""
        for side in ['white', 'red', 'green', 'yellow', 'orange', 'blue']:
            # Get the center color of the current side.
            center_bgr = self.result_state[side][4]

            # Compare the center color to all neighbors. If we come across a
            # different color, then we can assume the cube isn't solved yet.
            for bgr in self.result_state[side]:
                if center_bgr != bgr:
                    return False
        return True

    def run(self):
        key = cv2.waitKey(10) & 0xff
        #cv2.waitKey(10)函数会等待10毫秒，看是否有键盘输入。如果用户按下了键盘上的按键，
        #则返回该按键的ASCII码值。通过& 0xff操作，可以确保获取的是按键的低位8位ASCII码值。

        # if not self.calibrate_mode:#如果不是校准模式
        #     # Update the snapshot when space bar is pressed.
        #     if key == 32:#检测用户是否按下了空格键
        #         self.update_snapshot_state()

        # Toggle calibrate mode.
        if key == ord(CALIBRATE_MODE_KEY):
            self.reset_calibrate_mode()
            self.calibrate_mode = not self.calibrate_mode

        contours=[]
        my_w=30
        my_h=30
        for y in (40,110,180,250,320,390,457):
            for x in (138,208,278,348,418,488,553):
                contours.append((x,y,my_w,my_h))

        if len(contours) == 49:
            self.draw_contours(contours)
            
            if not self.calibrate_mode:
                self.update_preview_state(contours)
                pass
            elif key == 32 and self.done_calibrating is False:#空格键且还没校准完
                current_color = self.colors_to_calibrate[self.current_color_to_calibrate_index]
                (x, y, w, h) = contours[24]#选择中心块区域作为ROI
                roi = self.frame[y+7:y+h-7, x+14:x+w-14]
                avg_bgr = color_detector.get_dominant_color(roi)
                self.calibrated_colors[current_color] = avg_bgr
                self.current_color_to_calibrate_index += 1
                self.done_calibrating = self.current_color_to_calibrate_index == len(self.colors_to_calibrate)
                if self.done_calibrating:
                    color_detector.set_cube_color_pallete(self.calibrated_colors)
                    config.set_setting(CUBE_PALETTE, color_detector.cube_color_palette)
                pass
        if self.calibrate_mode:
            self.draw_current_color_to_calibrate()#画出上方的提示词
            self.draw_calibrated_colors()#画出左上方的颜色和文字
        else:
            # self.draw_current_language()
            self.draw_preview_stickers()
            # self.draw_snapshot_stickers()
            # self.draw_scanned_sides()
            # self.draw_2d_cube_state()


webcam = Webcam()
# webcam.run()
