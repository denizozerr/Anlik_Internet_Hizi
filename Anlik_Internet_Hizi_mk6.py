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

path = "Anlik_Internet_Hizi+Speed_Test"  # Kendi dizinine göre değiştir
files = glob.glob(os.path.join(path, "*.py"))  # Tüm .py dosyalarını bul

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content.replace("builtins", "builtins")  # Değiştir

    with open(file, "w", encoding="utf-8") as f:
        f.write(new_content)

print("Değiştirme işlemi tamamlandı.")


class InternetSpeedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anlık İnternet Hızı")
        self.root.geometry("400x300")
        self.root.resizable(True, True)
        self.root.iconbitmap(r"tatsumaki.ico")

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

        # CPU ve RAM etiketleri kutu içine alındı
        self.cpu_frame = Frame(self.frame, bg="#333333", bd=2, relief="solid")
        self.cpu_frame.pack(side="left", padx=10, pady=5)

        self.label_cpu = Label(self.cpu_frame, text="CPU: -%", font=("Calibri", 10), fg="white", bg="#333333")
        self.label_cpu.pack(side="left", padx=4)

        self.ram_frame = Frame(self.frame, bg="#333333", bd=2, relief="solid")
        self.ram_frame.pack(side="right", padx=10, pady=5)

        self.label_ram = Label(self.ram_frame, text="RAM: -%", font=("Calibri", 10), fg="white", bg="#333333")
        self.label_ram.pack(side="right", padx=4)

        self.update_resource_usage()

        self.label_download = Label(self.frame, text="Download: - MB/s", font=("Calibri", 16, "bold"), fg="cyan", bg="#1C1C1C")
        self.label_download.pack(pady=4, anchor='center')

        self.label_indir_mbps = Label(self.frame, text="Download: - Mbps", font=("Calibri", 10), fg="yellow",bg="#1C1C1C")
        self.label_indir_mbps.pack(pady=2, anchor='center')

        self.label_upload = Label(self.frame, text="Upload: - MB/s", font=("Calibri", 16, "bold"), fg="red", bg="#1C1C1C")
        self.label_upload.pack(pady=4, anchor='center')

        self.label_yukle_mbps = Label(self.frame, text="Upload: - Mbps", font=("Calibri", 10), fg="yellow", bg="#1C1C1C")
        self.label_yukle_mbps.pack(pady=2, anchor='center')

        self.label_speedtest = Label(self.frame, text="Speedtest Bekleniyor...", font=("Calibri", 12), fg="cyan", bg="#1C1C1C")
        self.label_speedtest.pack(pady=4, anchor='center')

        self.speedtest_button = Button(self.frame, text="Speedtest Başlat", command=self.run_speedtest, font=("Calibri", 12), bg="blue", fg="white")
        self.speedtest_button.pack(pady=5, anchor='center')

        # Verilerin görüntüleneceği uygulama verileri butonu
        self.app_data_button = Button(self.frame, text="Uygulama Verilerini Görüntüle", command=self.show_app_data, font=("Calibri", 12), bg="green", fg="white")
        self.app_data_button.pack(pady=10, anchor='center')

        self.label_imza = Label(self.frame, text="Made By Denizzr V.1.6", font=("Calibri", 10, "italic"), fg="magenta", bg="#1C1C1C")
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

            print(f"Download Speed: {download_speed / 1_000_000:.2f} Mbps")
            print(f"Upload Speed: {upload_speed / 1_000_000:.2f} Mbps")
            ping = st.results.ping
            self.label_speedtest.config(
                text=f"Ping: {ping:.2f} ms\nDownload: {download_speed:.2f} Mbps\nUpload: {upload_speed:.2f} Mbps",
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
        app_window.geometry("350x300")
        app_window.configure(bg="#1C1C1C")
        app_window.iconbitmap(r"tatsumaki.ico")

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

## Uygulamayı başlat
root = tk.Tk()
app = InternetSpeedApp(root)
root.mainloop()

