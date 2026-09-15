import pyautogui


class MouseController:

    def __init__(self, smoothing=0.12):

        self.screen_width, self.screen_height = pyautogui.size()

        self.smoothing = smoothing

        self.previous_x = None
        self.previous_y = None


    def move_cursor(self, x, y):

        # Keep cursor inside screen
        x = max(0.02, min(0.98, x))
        y = max(0.02, min(0.98, y))

        target_x = x * self.screen_width
        target_y = y * self.screen_height


        if self.previous_x is None:

            self.previous_x = target_x
            self.previous_y = target_y


        current_x = (
            self.previous_x
            +
            (target_x - self.previous_x)
            * self.smoothing
        )

        current_y = (
            self.previous_y
            +
            (target_y - self.previous_y)
            * self.smoothing
        )


        pyautogui.moveTo(
            int(current_x),
            int(current_y),
            duration=0
        )


        self.previous_x = current_x
        self.previous_y = current_y


    def left_click(self):

        pyautogui.click()


    def right_click(self):

        pyautogui.rightClick()


    def scroll(self, amount):

        if amount != 0:

            pyautogui.scroll(amount)


    def start_drag(self):

        pyautogui.mouseDown()


    def stop_drag(self):

        pyautogui.mouseUp()