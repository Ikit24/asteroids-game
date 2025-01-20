from constants import SCREEN_WIDTH, SCREEN_HEIGHT

def wrap_position(x, y):
    wrapped_x = x % SCREEN_WIDTH
    wrapped_y = y % SCREEN_HEIGHT
    return wrapped_x, wrapped_y