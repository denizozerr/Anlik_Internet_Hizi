import psutil
import tkinter as tk
from tkinter import Label, Frame, Listbox, Button
import threading
import time
import queue
import ctypes
import speedtest

class InternetSpeedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anlık İnternet Hızı")
        self.root.geometry("350x350")
        self.root.resizable(True, True)
        self.root.iconbitmap(r"C:\Users\Asus\Desktop\Anlik_Internet_Hizi+Speed_Test\tatsumaki.ico")

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

        self.label_cpu = Label(self.frame, text="CPU: -%", font=("Calibri", 10), fg="white", bg="#1C1C1C")
        self.label_cpu.pack(side="left", padx=4)

        self.label_ram = Label(self.frame, text="RAM: -%", font=("Calibri", 10), fg="white", bg="#1C1C1C")
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

        self.label_imza = Label(self.frame, text="Made By Denizzr", font=("Calibri", 10, "italic"), fg="magenta", bg="#1C1C1C")
        self.label_imza.pack(pady=4, anchor='center')

        self.app_usage_list = Listbox(self.frame, font=("Calibri", 12), fg="white", bg="#333333", height=8, selectmode=tk.SINGLE)
        self.app_usage_list.pack(pady=5, fill=tk.BOTH, expand=True)

        self.queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self.update_speed, daemon=True)
        self.thread.start()

        self.root.after(1000, self.update_ui)
        self.root.after(5000, self.update_app_usage)

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
            self.label_download.config(text=f"Download: {download:.2f} MB/s", fg="lime" if download > 0.20 else "cyan")
            self.label_upload.config(text=f"Upload: {upload:.2f} MB/s", fg="lime" if upload > 0.20 else "cyan")
            self.label_indir_mbps.config(text=f"Download: {download * 8:.2f} Mbps")
            self.label_yukle_mbps.config(text=f"Upload: {upload * 8:.2f} Mbps")

        if self.running:
            self.root.after(1000, self.update_ui)

    def update_app_usage(self):
        self.app_usage_list.delete(0, tk.END)
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
            self.app_usage_list.insert(tk.END, f"{app:20} : {data:8.2f} MB")

        if self.running:
            self.root.after(5000, self.update_app_usage)

    def update_resource_usage(self):
        self.label_cpu.config(text=f"CPU: {psutil.cpu_percent():.1f}%")
        self.label_ram.config(text=f"RAM: {psutil.virtual_memory().percent:.1f}%")
        self.root.after(1000, self.update_resource_usage)

    def run_speedtest(self):
        self.label_speedtest.config(text="Speedtest Başlatılıyor...", fg="yellow")  # Başlangıç mesajı
        self.speedtest_button.config(state=tk.DISABLED,text="Test Başladı. Lütfen Bekleyin...")  # Buton devre dışı bırakılır ve metin değiştirilir
        threading.Thread(target=self.perform_speedtest, daemon=True).start()

    def perform_speedtest(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download_speed = st.download() / (1024 * 1024)
            upload_speed = st.upload() / (1024 * 1024)
            ping = st.results.ping
            self.label_speedtest.config(
                text=f"Ping: {ping:.2f} ms\nDownload: {download_speed:.2f} Mbps\nUpload: {upload_speed:.2f} Mbps",fg="lime")
        except Exception as e:
            self.label_speedtest.config(text="Speedtest Hatası!", fg="red")
            print(f"Hata: {e}")
        finally:
            self.speedtest_button.config(state=tk.NORMAL,text="Speedtest Başlat")  # Buton tekrar etkinleştirilir ve eski metin gelir

#
if __name__ == "__main__":
    root = tk.Tk()
    app = InternetSpeedApp(root)
    root.mainloop()
