import time
from pygetwindow import getWindowsWithTitle
from pyautogui import screenshot
from pydlnadms import MediaServer

def get_active_window_title():
    active_windows = getWindowsWithTitle("")
    if active_windows:
        return active_windows[0].title
    return None

def start_dlna_server():
    server = MediaServer()
    server.add_file('screenshot.png', 'image/png')
    server.start()

    return server

def cast_to_dlna_server(server):
    while True:
        active_window_title = get_active_window_title()
        print(f"Active Window: {active_window_title}")

        if active_window_title and "Your Window Title" in active_window_title:
            # Capture the screen
            screenshot_path = 'screenshot.png'
            screenshot().save(screenshot_path)

            # Update the file in the DLNA server
            server.update_file('screenshot.png', screenshot_path)
            time.sleep(1)  # Adjust sleep time based on your needs

def main():
    server = start_dlna_server()
    cast_to_dlna_server(server)

if __name__ == "__main__":
    main()
