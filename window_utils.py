import win32gui
import win32con

def get_window_list():
    """获取所有可见窗口的列表"""
    windows = []
    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and not title.isspace():
                windows.append((hwnd, title))
    win32gui.EnumWindows(enum_windows_callback, None)
    return windows

def get_window_rect(hwnd):
    """获取窗口的位置和大小"""
    try:
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        width = rect[2] - x
        height = rect[3] - y
        return {'left': x, 'top': y, 'width': width, 'height': height}
    except:
        return None