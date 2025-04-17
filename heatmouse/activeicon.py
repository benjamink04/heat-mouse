# %% --- Imports -----------------------------------------------------------------------
import pathlib

import win32con
import win32gui
import win32ui
from PIL import Image

# %% --- Constants ---------------------------------------------------------------------
# %% PARENT_DIR
PARENT_DIR = pathlib.Path(__file__).parent.parent.absolute()


def get_active_window_icon(active_window):
    # Get handle to the foreground window
    output_path = None
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return
    # Get the icon handle
    icon_handle = win32gui.SendMessage(hwnd, win32con.WM_GETICON, win32con.ICON_BIG, 0)
    if not icon_handle:
        # Fallback to GetClassLong if WM_GETICON fails
        icon_handle = win32gui.GetClassLong(hwnd, win32con.GCL_HICON)
    if not icon_handle:
        return
    try:
        # Assume standard icon size (32x32 for ICON_BIG)
        width = 32
        height = 32
        # Create device contexts using win32ui
        hdc_screen = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hdc_mem = win32ui.CreateDCFromHandle(
            win32gui.CreateCompatibleDC(hdc_screen.GetHandleOutput())
        )
        # Create bitmap
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc_screen, width, height)
        # Select bitmap into memory DC
        old_bmp = hdc_mem.SelectObject(hbmp)
        # Draw the icon
        win32gui.DrawIconEx(
            hdc_mem.GetHandleOutput(),
            0,
            0,
            icon_handle,
            width,
            height,
            0,
            None,
            win32con.DI_NORMAL,
        )
        # Convert to PIL Image
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer(
            "RGBA",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr,
            "raw",
            "BGRA",
            0,
            1,
        )
        # Save the image
        output_path = str(PARENT_DIR.joinpath(f"database\\{active_window}.png"))
        img.save(output_path)
    except Exception as e:
        print(f"Error processing icon: {str(e)}")
    finally:
        # Cleanup
        try:
            if "old_bmp" in locals() and old_bmp:
                hdc_mem.SelectObject(old_bmp)  # Restore original bitmap
            if "hbmp" in locals() and hbmp:
                try:
                    win32gui.DeleteObject(hbmp.GetHandle())
                except Exception as e:
                    print(f"Error deleting bitmap: {str(e)}")
            if "hdc_mem" in locals() and hdc_mem:
                hdc_mem.DeleteDC()
            if "hdc_screen" in locals() and hdc_screen:
                hdc_screen.DeleteDC()
            if icon_handle:
                win32gui.DestroyIcon(icon_handle)
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
    return output_path
