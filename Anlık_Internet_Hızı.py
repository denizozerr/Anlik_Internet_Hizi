import psutil
import tkinter as tk
from tkinter import Label, Frame, Button, Toplevel
import threading
import time
import queue
import ctypes
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

class InternetSpeedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anlık İnternet Hızı")
        self.root.geometry("300x170")
        self.root.resizable(True, True)

        # Windows 10+ için başlık çubuğunu ve pencere temasını karanlık mod yap
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                                                       ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int(1)))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int(1)))
        except:
            pass

        self.root.configure(bg="#1C1C1C")
        self.frame = Frame(self.root, bg="#1C1C1C")
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.label_download = Label(self.frame, text="Download: - MB/s", font=("Calibri", 16, "bold"), fg="green", bg="#1C1C1C")
        self.label_download.pack(pady=4, anchor='center')

        self.label_download_mbps = Label(self.frame, text="Download: - Mbps", font=("Calibri", 10), fg="yellow", bg="#1C1C1C")
        self.label_download_mbps.pack(pady=2, anchor='center')

        self.label_upload = Label(self.frame, text="Upload: - MB/s", font=("Calibri", 16, "bold"), fg="red", bg="#1C1C1C")
        self.label_upload.pack(pady=4, anchor='center')

        self.label_upload_mbps = Label(self.frame, text="Upload: - Mbps", font=("Calibri", 10), fg="yellow", bg="#1C1C1C")
        self.label_upload_mbps.pack(pady=2, anchor='center')

        self.info_button = Button(self.frame, text="Bilgi", command=self.show_info, font=("Calibri", 10), fg="white", bg="#333333")
        self.info_button.pack(pady=10)

        self.queue = queue.Queue()
        self.running = True

        self.thread = threading.Thread(target=self.update_speed, daemon=True)
        self.thread.start()

        self.root.after(1000, self.update_ui)

        self.icon = self.create_icon()
        self.icon.run_detached()

    def create_icon(self):
        image = Image.new('RGB', (64, 64), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, 64, 64], fill="black")
        draw.text((10, 10), "Net", fill="white")

        menu = Menu(MenuItem("Çıkış", self.stop))
        icon = Icon("test_icon", image, menu=menu)
        return icon

    def update_speed(self):
        eski_veri = psutil.net_io_counters()
        while self.running:
            time.sleep(1)
            yeni_veri = psutil.net_io_counters()

            download_hizi = (yeni_veri.bytes_recv - eski_veri.bytes_recv) / (1024 * 1024)
            upload_hizi = (yeni_veri.bytes_sent - eski_veri.bytes_sent) / (1024 * 1024)

            self.queue.put((download_hizi, upload_hizi))
            eski_veri = yeni_veri

    def update_ui(self):
        while not self.queue.empty():
            download, upload = self.queue.get()

            self.update_label(self.label_download, download, "Download")
            self.update_label(self.label_upload, upload, "Upload")

            self.update_mbps_label(self.label_download_mbps, download)
            self.update_mbps_label(self.label_upload_mbps, upload)

        if self.running:
            self.root.after(1000, self.update_ui)

    def update_label(self, label, speed, label_type):
        number_color = self.get_number_color(speed)
        text = f"{label_type}: {speed:.2f} MB/s"
        label.config(text=text, fg=number_color)

    def update_mbps_label(self, label, speed):
        speed_mbps = speed * 8
        label.config(text=f"{speed_mbps:.2f} Mbps")

    def get_number_color(self, speed):
        return "lime" if speed > 0.20 else "cyan"

    def show_info(self):
        info_window = Toplevel(self.root)
        info_window.title("Bilgi Penceresi")
        info_window.geometry("400x200")
        info_window.configure(bg="#1C1C1C")

        info_text = """
        Bu uygulama, internet hızınızı anlık olarak ölçer ve 
        hem indirme hem de yükleme hızlarını görüntüler.
        """
        info_label = Label(info_window, text=info_text, font=("Calibri", 10), fg="white", bg="#1C1C1C", justify="left")
        info_label.pack(pady=20)

    def stop(self):
        self.running = False
        self.icon.stop()
        self.root.quit()


def start_gui():
    root = tk.Tk()
    app = InternetSpeedApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()

<<<<<<< HEAD
#
=======

>>>>>>> 3ba151d8efcc1cb2a4c72da4968d77949f138fa5
if __name__ == "__main__":
    start_gui()
