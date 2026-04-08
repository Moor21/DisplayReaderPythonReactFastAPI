import cv2
import numpy as np
from ImageProcessing import ImageProcessing


class DigitBoxes:
    def __init__(self, display_image, proc: ImageProcessing):
        self.display_image = display_image
        self.proc = proc
        self.binary_height = None
        self.pureCroppedDisplay = None
        self.SEG_PATTERNS = {
            "0": (1, 1, 1, 1, 1, 1, 0),
            "2": (1, 1, 0, 1, 1, 0, 1),
            "3": (1, 1, 1, 1, 0, 0, 1),
            "4": (0, 1, 1, 0, 0, 1, 1),
            "5": (1, 0, 1, 1, 0, 1, 1),
            "6": (1, 0, 1, 1, 1, 1, 1),
            "7": (1, 0, 1, 0, 0, 1, 0),
            "8": (1, 1, 1, 1, 1, 1, 1),
            "9": (1, 1, 1, 1, 0, 1, 1),
            "U": (0, 0, 1, 1, 1, 0, 0),
            "P": (0, 1, 0, 0, 1, 1, 0),
            "C": (0, 0, 1, 1, 1, 0, 1),
        }

    def loadPureImage(self, pure_display_image):
        pureCroppedDisplay = pure_display_image.copy()
        thresh_height = int(pure_display_image.shape[0] * 0.25)
        thresh_width = int(pure_display_image.shape[1] * 0.07)

        h, w = pureCroppedDisplay.shape[:2]
        y1 = max(0, thresh_height)
        y2 = min(h, h - thresh_height)
        x1 = max(0, thresh_width)
        x2 = min(w, w - thresh_width)

        if y2 > y1 and x2 > x1:
            pureCroppedDisplay = pureCroppedDisplay[y1:y2, x1:x2]

        self.pureCroppedDisplay = pureCroppedDisplay

    def getDisplayThresholdImage(self):
        thresholdDisplay = self.proc.getThresholdImage(
            self.display_image, (5, 5), 60, (1, 1)
        )

        thresh_height = int(thresholdDisplay.shape[0] * 0.25)
        thresh_width = int(thresholdDisplay.shape[1] * 0.07)

        h, w = thresholdDisplay.shape[:2]
        y1 = max(0, thresh_height)
        y2 = min(h, h - thresh_height)
        x1 = max(0, thresh_width)
        x2 = min(w, w - thresh_width)

        if y2 > y1 and x2 > x1:
            thresholdDisplay = thresholdDisplay[y1:y2, x1:x2]

        cv2.imshow("Thresholded display", thresholdDisplay)
        return thresholdDisplay

    def specialSymbolAnalys(self, binary, grouped):
        if binary is None or binary.size == 0:
            return "?"

        if not grouped:
            return "?"

        box = grouped[0]
        img_h = self.binary_height if self.binary_height is not None else binary.shape[0]

        start_x, end_x = box
        x1 = int(start_x)
        x2 = int(end_x)
        y1 = 0
        y2 = int(img_h)

        digit_width = x2 - x1 + 1
        digit_height = y2 - y1

        if digit_width <= 0 or digit_height <= 0:
            return "?"

        seg_t = max(1, digit_width // 4)
        mid_y = y1 + digit_height // 2

        one_segment = ((x1 + seg_t, y1), (x2 - seg_t, y1 + seg_t))
        two_segment = ((x2 - seg_t, y1 + seg_t), (x2, mid_y - seg_t // 2))
        three_segment = ((x2 - seg_t, mid_y + seg_t // 2), (x2, y2 - seg_t))
        four_segment = ((x1 + seg_t, y2 - seg_t), (x2 - seg_t, y2))
        five_segment = ((x1, mid_y + seg_t // 2), (x1 + seg_t, y2 - seg_t))
        six_segment = ((x1, y1 + seg_t + seg_t // 2), (x1 + seg_t, mid_y))
        seven_segment = ((x1 + seg_t, mid_y - seg_t // 4), (x2 - seg_t, mid_y + seg_t // 2))

        places_for_checking = [
            one_segment,
            two_segment,
            three_segment,
            four_segment,
            five_segment,
            six_segment,
            seven_segment,
        ]


        segment_dict = {}

        for idx, segment in enumerate(places_for_checking):
            (sx1, sy1), (sx2, sy2) = segment

            x_left = max(0, min(sx1, sx2))
            x_right = min(binary.shape[1], max(sx1, sx2))
            y_top = max(0, min(sy1, sy2))
            y_bottom = min(binary.shape[0], max(sy1, sy2))

            fill_ratio = 0.0

            if x_right > x_left and y_bottom > y_top:
                segment_roi = binary[y_top:y_bottom, x_left:x_right]
                segment_roi_area = segment_roi.shape[0] * segment_roi.shape[1]

                if segment_roi_area > 0:
                    fill_ratio = cv2.countNonZero(segment_roi) / segment_roi_area

            segment_dict[idx] = 1 if fill_ratio > 0.3 else 0

        segment_tuple = tuple(segment_dict[i] for i in range(7))
        best_score = -1
        best_symbol = "?"

        for candidate, pattern in self.SEG_PATTERNS.items():
            score = sum(1 for a, b in zip(segment_tuple, pattern) if a == b)
            if score > best_score:
                best_score = score
                best_symbol = candidate

        symbol = best_symbol if best_score > 6 else "?"
        return symbol

    def getWholeDigitString(self, binary):
        if binary is None or binary.size == 0:
            return ""

        self.binary_height = binary.shape[0]
        projection_matrix = (binary > 0).sum(axis=0)

        proj_thresh = int(self.binary_height * 0.1)
        mask = projection_matrix > proj_thresh
        print("Mask: ", mask)
        spans = []
        in_run = False
        start = 0

        for i, v in enumerate(mask):
            if v and not in_run:
                start = i
                in_run = True
            elif not v and in_run:
                spans.append((start, i - 1))
                in_run = False

        if in_run:
            spans.append((start, len(mask) - 1))

        if not spans:
            return ""

        grouped = []
        latest_start, latest_end = spans[0]

        grouped_threshold = binary.shape[1] * 0.05


        for start, end in spans[1:]:
            gap = start - latest_end
            width = end - start + 1

            if gap < grouped_threshold and width < grouped_threshold:
                latest_end = max(latest_end, end)
            else:
                grouped.append((latest_start, latest_end))
                latest_start, latest_end = start, end

        grouped.append((latest_start, latest_end))

        if not grouped:
            return ""

        spec_sym = self.specialSymbolAnalys(binary, grouped)
        print("Spec_sym: ", spec_sym)
        whole_digit = None
        if spec_sym == "U":
            digit_groups = grouped[1:] if len(grouped) > 1 else []
            print("Digit_groups: ", digit_groups)
            whole_digit = self.digitBoxAnalys(binary, digit_groups)

    
        return whole_digit

    def insertPointIntoNumberString(self, left_digit_index, whole_digit):
        result = whole_digit

        if whole_digit is None:
            return ""

        if left_digit_index is not None:
            s = str(whole_digit)

            # защита от выхода за границы
            if 0 <= left_digit_index < len(s):
                result = s[:left_digit_index + 1] + "." + s[left_digit_index + 1:]

        return result

    def _pointDetection(self, projection_vector, binary, grouped):
        if binary is None or binary.size == 0:
            return None

        if not grouped:
            return None

        first_group_width = grouped[0][1] - grouped[0][0] + 1
        possible_point_width = max(1, int(first_group_width * 0.15))
        possible_point_height = max(1, int(self.binary_height * 0.1))
        print("Projection_vector: ", projection_vector)
        point_mask = (projection_vector > 2) & (projection_vector < 5)
        print("Point_mask: ", point_mask)
        point_cand = []
        isRun = False
        start = 0

        for i, v in enumerate(point_mask):
            if v and not isRun:
                start = i
                isRun = True
            elif not v and isRun:
                point_cand.append((start, i - 1))
                isRun = False

        if isRun:
            point_cand.append((start, len(point_mask) - 1))
            isRun = False


        if not point_cand:
            return None

        point_cands_ratio = {}

        for idx, point in enumerate(point_cand):
            point_width = point[1] - point[0] + 1
            print("Point_cand: ", point_cand)
            print("Point_width: ", point_width)
            print("Possible_point_width: ", possible_point_width)
            print("Possible_point_height: ", possible_point_height)
            if possible_point_width - 2 <= point_width <= possible_point_width + 2:
                point_x1 = point[0]
                point_x2 = point[1] + 1  # чтобы правая граница включалась срезом
                point_y1 = max(0, self.binary_height - possible_point_height)
                point_y2 = self.binary_height
                print("Point_y1: ",point_y1)
                print("Point_y2: ", point_y2)
                point_roi = binary[point_y1:point_y2, point_x1:point_x2]
                cv2.imshow("Point_roi", point_roi)
                print("Point_roi: ", point_roi)
                point_roi_area = point_roi.shape[0] * point_roi.shape[1]
                print("point_roi_area: ", point_roi_area )
                fill_ratio = 0.0
                if point_roi_area > 0:
                    print("cv2.countNonZero(point_roi): ", cv2.countNonZero(point_roi))
                    fill_ratio = cv2.countNonZero(point_roi) / point_roi_area
                print("Fill_ratio: ", fill_ratio)
                point_cands_ratio[idx] = fill_ratio
            else:
                point_cands_ratio[idx] = 0.0


        if not point_cands_ratio:
            return None
        print("points_cand_ratio: ", point_cands_ratio)
        best_point_idx = max(point_cands_ratio, key=point_cands_ratio.get)
        print("Best_point_idx: ", best_point_idx)
        if point_cands_ratio[best_point_idx] <= 0:
            return None

        best_point_place = point_cand[best_point_idx]
        print("Best_point_place: ", best_point_place)
        left_digit_index = None
        point_center = (best_point_place[1] + best_point_place[0]) // 2
        print("Point_center: ", point_center)
        best_gap = float("inf")
        for i, digit in enumerate(grouped):
            left_digit = digit
            print("Left digit right side: ", left_digit[1])
            if  left_digit[1]-2 < point_center < 2+left_digit[1]:
                gap = abs(point_center - left_digit[1])
                if gap <= 2 and gap < best_gap:
                    best_gap = gap
                    left_digit_index = i

        return left_digit_index

    def drawDigitBoxesBySpans(self, threshold_image, spans):
        display_image_digit_boxes = threshold_image.copy()
        box_height = threshold_image.shape[0]

        for span in spans:
            cv2.rectangle(
                display_image_digit_boxes,
                (span[0], 0),
                (span[1], box_height),
                (120, 255, 120),
                3,
            )

        return display_image_digit_boxes

    def digitBoxAnalys(self, binary, grouped):
        if binary is None or binary.size == 0:
            return ""

        if not grouped:
            return ""

        whole_digit = ""
        segment_rectangles = binary.copy()
        img_h = self.binary_height if self.binary_height is not None else binary.shape[0]

        for i, box in enumerate(grouped):
            segment_dict = {}

            start_x, end_x = box
            x1 = int(start_x)
            x2 = int(end_x)
            y1 = 0
            y2 = int(img_h)

            digit_width = x2 - x1 + 1
            digit_height = y2 - y1

            if digit_width <= 0 or digit_height <= 0:
                whole_digit += "?"
                continue
            #-----флаг для типа числа----#
            digit_type = 0
            #-----Настраиваем параметры для определения местностей проверки каждого сегмента----#
            seg_t = max(1, digit_width // 4)
            mid_y = y1 + digit_height // 2
            if digit_width>12:
                #-----Определяем верхний левый и правый нижний угол каждого сегмента для стандартного числа (кроме 1)-----#
                one_segment = ((x1+seg_t , y1+seg_t), (x2 - seg_t, y1 + seg_t*2))
                two_segment = ((x2 - seg_t, y1 + seg_t), (x2, mid_y - seg_t // 2))
                three_segment = ((x2 - seg_t, mid_y + seg_t // 2), (x2, y2 - seg_t))
                four_segment = ((x1 + seg_t, y2 - seg_t), (x2 - seg_t, y2))
                five_segment = ((x1, mid_y + seg_t // 2), (x1 + seg_t, y2 - seg_t))
                six_segment = ((x1, y1 + seg_t + seg_t // 2), (x1 + seg_t, mid_y))
                seven_segment = ((x1 + seg_t, mid_y - seg_t // 4), (x2 - seg_t, mid_y + seg_t // 2))
                #-------Добавляем place каждого сегмента в массив places_for_checking -----#
            
                places_for_checking = [
                    one_segment,
                    two_segment,
                    three_segment,
                    four_segment,
                    five_segment,
                    six_segment,
                    seven_segment,
                ]
            elif digit_width < 12:
                digit_type = 1
                one_segment = ((x1+seg_t,y1),(x2-seg_t, mid_y))
                two_segment = ((x1+seg_t, mid_y),(x2-seg_t, y2))

                places_for_checking = [
                    one_segment,
                    two_segment
                ]
                
            #-----Отрисовка place-а для проверки каждого сегмента на бинарнике----#
            for point in places_for_checking:
                cv2.rectangle(segment_rectangles, point[0], point[1], (255,255,255),1)
            #-----Проверка каждого сегмента на заполнинность - использование best_score----#
            for idx, segment in enumerate(places_for_checking):
                #-----определение углов бокса для проверки-----#
                (sx1, sy1), (sx2, sy2) = segment

                x_left = max(0, min(sx1, sx2))
                x_right = min(binary.shape[1], max(sx1, sx2))
                y_top = max(0, min(sy1, sy2))
                y_bottom = min(binary.shape[0], max(sy1, sy2))

                fill_ratio = 0.0

                if x_right > x_left and y_bottom > y_top:
                    segment_roi = binary[y_top:y_bottom, x_left:x_right]
                    segment_roi_area = segment_roi.shape[0] * segment_roi.shape[1]

                    if segment_roi_area > 0:
                        fill_ratio = cv2.countNonZero(segment_roi) / segment_roi_area

                segment_dict[idx] = 1 if fill_ratio > 0.3 else 0
            #-----превращаем dict в tuple для удобного сравнения-----#
            if digit_type == 0:
                segment_tuple = tuple(segment_dict[i] for i in range(7))
            elif digit_type == 1:
                segment_tuple = tuple(segment_dict[i] for i in range(2))
            print("Segment_tuple: ", segment_tuple)

            #-----определяем число с погрешностью в один сегмент----#
            best_score = -1
            best_digit = None
            if digit_type == 0:
                for digit, pattern in self.SEG_PATTERNS.items():
                    score = sum(1 for a, b in zip(segment_tuple, pattern) if a == b)
                    if score > best_score:
                        best_digit = digit
                        best_score = score

                if best_score >= 6 and best_digit is not None:
                    whole_digit += best_digit
                else:
                    whole_digit += "?"
            elif digit_type == 1:
                if segment_tuple[0] == 1 and segment_tuple[1] == 1:
                    whole_digit += "1"

        cv2.imshow("segments", segment_rectangles)
        return whole_digit