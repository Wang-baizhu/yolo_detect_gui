import win32gui
import win32con

def get_window_list():
    """获取所有可见窗口的列表"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and not title.isspace():  # 排除空标题窗口
                windows.append((hwnd, title))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return sorted(windows, key=lambda x: x[1].lower())  # 按标题排序

def get_window_rect(hwnd):
    """获取窗口的位置和大小"""
    try:
        # 获取窗口位置
        rect = win32gui.GetWindowRect(hwnd)
        x = rect[0]
        y = rect[1]
        w = rect[2] - x
        h = rect[3] - y
        
        # 如果窗口最小化，返回None
        if win32gui.IsIconic(hwnd):
            return None
            
        # 返回mss格式的区域
        return {
            "left": x,
            "top": y,
            "width": w,
            "height": h
        }
    except:
        return None 