import psutil
import tkinter as tk
from tkinter import Label, Frame, Listbox, Button, Toplevel
import threading
import time
import queue
import ctypes
import speedtest
import os
import glob

path = "Anlik_Internet_Hizi+Speed_Test"
files = glob.glob(os.path.join(path, "*.py"))  # Tüm .py dosyalarını bul
"""
for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content.replace("builtins", "builtins")  #__builtin__ fonksiyonu python 2 ile çalışıp python 3 ile çalışmadığından değiştirdik buradan manuel olarak kütüphaneden de değiştirildi

    with open(file, "w", encoding="utf-8") as f:
        f.write(new_content)

print("Değiştirme işlemi tamamlandı.")
"""

class InternetSpeedApp:
    def __init__(self, root):

        self.root = root
        self.root.title("Anlık İnternet Hızı")
        # Pencereyi ekranın ortasında başlatmak için
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Ortada olacak şekilde pencereyi konumlandır
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        # Pencereyi bu pozisyonda aç
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.geometry("400x300")
        self.root.resizable(True, True)
        self.root.iconbitmap(r"tatsumaki.ico")
        self.root.attributes('-topmost', True)



        #%% windows karanlık mod title için
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                                                       ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int(1)))
        except:
            pass

        self.root.configure(bg="#1C1C1C")
        self.frame = Frame(self.root, bg="#1C1C1C")
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.cpu_frame = Frame(self.frame, bg="#333333", bd=2, relief="solid")
        self.cpu_frame.pack(side="left", padx=10, pady=5)

        self.label_cpu = Label(self.cpu_frame, text="CPU: -%", font=("Calibri", 10), fg="white", bg="#333333")
        self.label_cpu.pack(side="left", padx=4)

        self.ram_frame = Frame(self.frame, bg="#333333", bd=2, relief="solid")
        self.ram_frame.pack(side="right", padx=10, pady=5)

        self.label_ram = Label(self.ram_frame, text="RAM: -%", font=("Calibri", 10), fg="white", bg="#333333")
        self.label_ram.pack(side="right", padx=4)

        self.update_resource_usage()

        self.label_download = Label(self.frame, text="Download: - MB/s", font=("Calibri", 16, "bold"), fg="cyan", bg="#333333", relief="solid", bd=2)
        self.label_download.pack(pady=4, anchor='center')

        self.label_indir_mbps = Label(self.frame, text="Download: - Mbps", font=("Calibri", 10), fg="yellow",bg="#333333", relief="solid", bd=2)
        self.label_indir_mbps.pack(pady=2, anchor='center')

        self.label_upload = Label(self.frame, text="Upload: - MB/s", font=("Calibri", 16, "bold"), fg="red", bg="#333333", relief="solid", bd=2)
        self.label_upload.pack(pady=4, anchor='center')

        self.label_yukle_mbps = Label(self.frame, text="Upload: - Mbps", font=("Calibri", 10), fg="yellow", bg="#333333", relief="solid", bd=2)
        self.label_yukle_mbps.pack(pady=2, anchor='center')

        self.label_speedtest = Label(self.frame, text="Speedtest Bekleniyor...", font=("Calibri", 12), fg="cyan", bg="#1C1C1C")
        self.label_speedtest.pack(pady=4, anchor='center')

        self.speedtest_button = Button(self.frame, text="Speedtest Başlat", command=self.run_speedtest, font=("Calibri", 12), bg="dark blue", fg="white")
        self.speedtest_button.pack(pady=5, anchor='center')

        # Verilerin görüntüleneceği uygulama verileri butonu
        self.app_data_button = Button(self.frame, text="Uygulama Verilerini Görüntüle", command=self.show_app_data, font=("Calibri", 12), bg="green", fg="white")
        self.app_data_button.pack(pady=10, anchor='center')

        self.label_imza = Label(self.frame, text="Made By Denizzr \n v.1.7", font=("Calibri", 10, "italic"), fg="magenta", bg="#1C1C1C")
        self.label_imza.pack(pady=4, anchor='center')

        self.queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self.update_speed, daemon=True)
        self.thread.start()

        self.root.after(1000, self.update_ui)

    def update_speed(self):
        old_data = psutil.net_io_counters()
        while self.running:
            time.sleep(1)
            new_data = psutil.net_io_counters()
            download_speed = (new_data.bytes_recv - old_data.bytes_recv) / (1024 * 1024)
            upload_speed = (new_data.bytes_sent - old_data.bytes_sent) / (1024 * 1024)
            self.queue.put((download_speed, upload_speed))
            old_data = new_data

    def update_ui(self):
        while not self.queue.empty():
            download, upload = self.queue.get()
            self.label_download.config(text=f"Download: {download:.2f} MB/s", fg="lime" if download >= 0.20 else "cyan")
            self.label_upload.config(text=f"Upload: {upload:.2f} MB/s", fg="lime" if upload >= 0.20 else "cyan")
            self.label_indir_mbps.config(text=f"Download: {download * 8:.2f} Mbps")
            self.label_yukle_mbps.config(text=f"Upload: {upload * 8:.2f} Mbps")

        if self.running:
            self.root.after(1000, self.update_ui)


    def update_resource_usage(self):
        self.label_cpu.config(text=f"CPU: {psutil.cpu_percent():.1f}%")
        self.label_ram.config(text=f"RAM: {psutil.virtual_memory().percent:.1f}%")
        self.root.after(1000, self.update_resource_usage)

    def run_speedtest(self):
        self.label_speedtest.config(text="Speedtest Başlatılıyor...", fg="yellow")  # Başlangıç mesajı
        self.speedtest_button.config(state=tk.DISABLED, text="Test Başladı. Lütfen Bekleyin...")  # Buton devre dışı bırakılır ve metin değiştirilir
        threading.Thread(target=self.perform_speedtest, daemon=True).start()

    def perform_speedtest(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download_speed = st.download()
            upload_speed = st.upload()

            print(f"Download Speed: {download_speed / 1_000_000.0:.2f} Mbps")
            print(f"Upload Speed: {upload_speed / 1_000_000.0:.2f} Mbps")
            ping = st.results.ping
            self.label_speedtest.config(
                text=f"Ping: {ping:.2f} ms\nDownload: {download_speed / 1e6:.2f} Mbps\nUpload: {upload_speed / 1e6:.2f} Mbps",
                fg="lime")
        except speedtest.SpeedtestException as e:
            self.label_speedtest.config(text=f"Speedtest Hatası: {e}", fg="red")
            print(f"Speedtest Hatası: {e}")
        except Exception as e:
            self.label_speedtest.config(text=f"Genel Hata: {e}", fg="red")
            print(f"Genel Hata: {e}")
        finally:
            self.speedtest_button.config(state=tk.NORMAL,
                                         text="Speedtest Başlat")  # Buton tekrar etkinleştirilir ve eski metin gelir

    def show_app_data(self):
        # Yeni pencereyi açarak uygulama verilerini göstermek için
        app_window = Toplevel(self.root)
        app_window.title("Uygulama Verileri")
        # Pencereyi ekranın ortasında başlatmak için
        window_width = 350
        window_height = 300
        screen_width = app_window.winfo_screenwidth()
        screen_height = app_window.winfo_screenheight()

        # Ortada olacak şekilde pencereyi konumlandır
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        # Pencereyi bu pozisyonda aç
        app_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        app_window.configure(bg="#1C1C1C")
        app_window.iconbitmap(r"tatsumaki.ico")
        app_window.attributes('-topmost', True)


        # Menü çubuğu oluştur
        menu_bar = tk.Menu(app_window)
        app_window.config(menu=menu_bar)

        # Bilgi menüsü
        bilgi_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Bilgi", menu=bilgi_menu)
        bilgi_menu.add_command(label="Hakkında", command=lambda: show_about_window(app_window))

        # Hakkında penceresini açan fonksiyon
        def show_about_window(parent):
            about_window = Toplevel(parent)
            about_window.title("Hakkında")
            window_width = 300
            window_height = 150
            screen_width = about_window.winfo_screenwidth()
            screen_height = about_window.winfo_screenheight()

            # Ortada olacak şekilde pencereyi konumlandır
            x_position = (screen_width // 2) - (window_width // 2)
            y_position = (screen_height // 2) - (window_height // 2)

            # Pencereyi bu pozisyonda aç
            about_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
            about_window.configure(bg="#1C1C1C")
            about_window.iconbitmap(r"tatsumaki.ico")
            about_window.attributes('-topmost', True)

            # Grid yapılandırması
            about_window.grid_rowconfigure(0, weight=1)
            about_window.grid_rowconfigure(1, weight=1)
            about_window.grid_columnconfigure(0, weight=1)

            label_info = Label(about_window, text="Ağ kullanımı penceresinde sistem başladığından itibaren "
                                                  "uygulamaların kullandığı verileri göstermektedir. \n\n"
                                                  "Made By Denizzr\n v.1.7",
                               font=("Calibri", 12), fg="white", bg="#1C1C1C", justify="center", wraplength=280)
            label_info.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            close_button = Button(about_window, text="Kapat", command=about_window.destroy,
                                  font=("Calibri", 10), bg="red", fg="white", width=10, height=2)

        try:
            app_window.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(app_window.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                                                       ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int(1)))
        except:
            pass

        label = Label(app_window, text="Ağ Kullanımı:", font=("Calibri", 14), fg="white", bg="#1C1C1C")
        label.pack(pady=10)

        listbox = Listbox(app_window, font=("Calibri", 12), fg="white", bg="#333333", height=8)
        listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        processes = [(p.info['name'], p.info['pid']) for p in psutil.process_iter(['name', 'pid'])]
        usage_data = {}
        for name, pid in processes:
            try:
                net_io = psutil.Process(pid).io_counters()
                total_data = (net_io.read_bytes + net_io.write_bytes) / (1024 * 1024)
                if total_data > 100:
                    usage_data[name] = total_data
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        for app, data in sorted(usage_data.items(), key=lambda x: x[1], reverse=True):
            listbox.insert(tk.END, f"{app:20} : {data:8.2f} MB")

        app_window.mainloop()


### Uygulamayı başlat
root = tk.Tk()
app = InternetSpeedApp(root)
root.mainloop()

