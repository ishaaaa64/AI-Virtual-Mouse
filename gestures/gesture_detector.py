import math
import time


class GestureDetector:

    def __init__(self):

        # =====================================================
        # PINCH DISTANCES
        # =====================================================

        self.left_threshold = 0.060
        self.right_threshold = 0.060

        self.scroll_threshold = 0.080


        # =====================================================
        # LEFT PINCH
        # =====================================================

        self.left_pinch_start = None

        self.left_click_done = False

        self.dragging = False


        # =====================================================
        # RIGHT CLICK
        # =====================================================

        self.right_pinch_start = None

        self.right_click_done = False


        # =====================================================
        # CLICK SETTINGS
        # =====================================================

        self.click_delay = 0.20

        self.drag_delay = 0.65


        # =====================================================
        # SCROLL
        # =====================================================

        self.previous_scroll_y = None


    # =========================================================
    # DISTANCE
    # =========================================================

    def distance(self, p1, p2):

        dx = p1.x - p2.x
        dy = p1.y - p2.y

        return math.sqrt(
            dx * dx +
            dy * dy
        )


    # =========================================================
    # LEFT PINCH
    # =========================================================

    def left_pinch(self, hand):

        return self.distance(
            hand[4],
            hand[8]
        ) < self.left_threshold


    # =========================================================
    # RIGHT PINCH
    # =========================================================

    def right_pinch(self, hand):

        return self.distance(
            hand[4],
            hand[12]
        ) < self.right_threshold


    # =========================================================
    # SCROLL
    # =========================================================

    def scroll_mode(self, hand):

        return self.distance(
            hand[8],
            hand[12]
        ) < self.scroll_threshold


    # =========================================================
    # UPDATE LEFT PINCH
    # =========================================================

    def update_left_pinch(self, hand):

        now = time.time()

        pinch = self.left_pinch(hand)


        # -----------------------------------------------------
        # Pinch started
        # -----------------------------------------------------

        if pinch:

            if self.left_pinch_start is None:

                self.left_pinch_start = now

                self.left_click_done = False


                return "PINCH_START"


            duration = (
                now -
                self.left_pinch_start
            )


            # -------------------------------------------------
            # Start drag
            # -------------------------------------------------

            if (
                duration >= self.drag_delay
                and not self.dragging
            ):

                self.dragging = True

                return "START_DRAG"


            # -------------------------------------------------
            # Continue drag
            # -------------------------------------------------

            if self.dragging:

                return "DRAGGING"


            # -------------------------------------------------
            # Waiting for click / drag
            # -------------------------------------------------

            return "PINCHING"


        # -----------------------------------------------------
        # Pinch released
        # -----------------------------------------------------

        else:

            if self.left_pinch_start is not None:

                duration = (
                    now -
                    self.left_pinch_start
                )


                # ---------------------------------------------
                # Drag released
                # ---------------------------------------------

                if self.dragging:

                    self.dragging = False

                    self.left_pinch_start = None

                    return "STOP_DRAG"


                # ---------------------------------------------
                # Short pinch = click
                # ---------------------------------------------

                if (
                    duration >= self.click_delay
                    and not self.left_click_done
                ):

                    self.left_click_done = True

                    self.left_pinch_start = None

                    return "LEFT_CLICK"


            self.left_pinch_start = None

            return "NONE"


    # =========================================================
    # RIGHT CLICK
    # =========================================================

    def update_right_pinch(self, hand):

        now = time.time()

        pinch = self.right_pinch(hand)


        if pinch:

            if self.right_pinch_start is None:

                self.right_pinch_start = now

                self.right_click_done = False

                return "RIGHT_PINCH"


            duration = (
                now -
                self.right_pinch_start
            )


            if (
                duration >= self.click_delay
                and not self.right_click_done
            ):

                self.right_click_done = True

                return "RIGHT_CLICK"


            return "RIGHT_PINCH"


        else:

            self.right_pinch_start = None

            return "NONE"


    # =========================================================
    # SCROLL AMOUNT
    # =========================================================

    def get_scroll_amount(self, hand):

        current_y = (
            hand[8].y +
            hand[12].y
        ) / 2


        if self.previous_scroll_y is None:

            self.previous_scroll_y = current_y

            return 0


        difference = (
            self.previous_scroll_y -
            current_y
        )


        self.previous_scroll_y = current_y


        if abs(difference) < 0.004:

            return 0


        amount = int(
            difference * 180
        )


        amount = max(
            -10,
            min(10, amount)
        )


        return amount


    # =========================================================
    # RESET SCROLL
    # =========================================================

    def reset_scroll(self):

        self.previous_scroll_y = None