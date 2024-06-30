import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress
import psutil
import platform
from datetime import datetime

# Función para representar tamaños en bits.
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

class SubFormulario1(tk.Toplevel):
     def __init__(self, master=None):
        super().__init__(master)
        self.title("SubFormulario 1")
        # Add your widgets for SubFormulario 1 here
        label = ttk.Label(self, text="This is SubFormulario 1")
        label.pack(padx=20, pady=20)

class SubFormulario2(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("SubFormulario 2")
        # Add your widgets for SubFormulario 2 here
        label = ttk.Label(self, text="This is SubFormulario 2")
        label.pack(padx=20, pady=20)

class SubFormulario3(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("SubFormulario 3")
        # Add your widgets for SubFormulario 3 here
        label = ttk.Label(self, text="This is SubFormulario 3")
        label.pack(padx=20, pady=20)

class SubFormularioSubneteo(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Calculadora de Subredes")

        tk.Label(self, text="Dirección IP:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_ip = tk.Entry(self)
        self.entry_ip.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="Máscara de Subred:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_subnet_mask = tk.Entry(self)
        self.entry_subnet_mask.grid(row=1, column=1, padx=10, pady=5)

        calculate_button = tk.Button(self, text="Calcular", command=self.calculate_subnet)
        calculate_button.grid(row=2, columnspan=2, padx=10, pady=10)

        columns = ("Atributo", "Valor")
        self.table = ttk.Treeview(self, columns=columns, show='headings')
        self.table.heading("Atributo", text="Atributo")
        self.table.heading("Valor", text="Valor")
        self.table.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')

    def ip_to_binary(self, ip):
        return '.'.join([f'{int(octet):08b}' for octet in ip.split('.')])

    def get_network_class(self, ip):
        first_octet = int(ip.split('.')[0])
        if first_octet >= 1 and first_octet <= 126:
            return 'Clase A'
        elif first_octet >= 128 and first_octet <= 191:
            return 'Clase B'
        elif first_octet >= 192 and first_octet <= 223:
            return 'Clase C'
        elif first_octet >= 224 and first_octet <= 239:
            return 'Clase D'
        else:
            return 'Clase E'

    def calculate_subnet(self):
        ip_str = self.entry_ip.get()
        subnet_mask_str = self.entry_subnet_mask.get()

        try:
            ip = ipaddress.ip_interface(f'{ip_str}/{subnet_mask_str}')
            network = ip.network
            netmask = network.netmask
            broadcast = network.broadcast_address
            first_usable = network.network_address + 1
            last_usable = broadcast - 1
            wildcard_mask = ipaddress.ip_interface(f'0.0.0.0/{subnet_mask_str}').hostmask
            num_hosts = network.num_addresses - 2

            results = {
                "Dirección IP": ip_str,
                "Máscara de Subred": f'{netmask} ({ip.network.prefixlen})',
                "Dirección de Red": str(network.network_address),
                "Dirección de Broadcast": str(broadcast),
                "Primera Dirección IP Utilizable": str(first_usable),
                "Última Dirección IP Utilizable": str(last_usable),
                "Número de Hosts": f'{network.num_addresses} ({num_hosts} utilizables)',
                "Máscara Wildcard": str(wildcard_mask),
                "Representación Binaria de la IP": self.ip_to_binary(ip_str),
                "Representación Binaria de la Máscara de Subred": self.ip_to_binary(str(netmask)),
                "Clase de Red": self.get_network_class(ip_str)
            }

            # Limpiar datos existentes en el TreeView
            for child in self.table.get_children():
                self.table.delete(child)

            # Insertar nuevos datos en el TreeView
            for key, value in results.items():
                self.table.insert('', 'end', values=(key, value))

        except Exception as e:
            messagebox.showerror("Error", f"Hubo un error al calcular la subred: {e}")

class SubFormularioAnalizadorPC(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Analizador de PC")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Información del sistema").pack(padx=10, pady=10)

        self.system_info_tree = ttk.Treeview(self, columns=("Atributo", "Valor"), show='headings')
        self.system_info_tree.heading("Atributo", text="Atributo")
        self.system_info_tree.heading("Valor", text="Valor")
        self.system_info_tree.pack(padx=10, pady=10)

        self.get_system_info()
        self.get_cpu_info()
        self.get_memory_info()
        self.get_disk_info()
        self.get_network_info()

    def get_system_info(self):
        uname = platform.uname()
        system_info = [
            ("Sistema", uname.system),
            ("Nombre de nodo", uname.node),
            ("Release", uname.release),
            ("Versión", uname.version),
            ("Máquina", uname.machine),
            ("Procesador", uname.processor)
        ]

        for item in system_info:
            self.system_info_tree.insert('', 'end', values=item)

    def get_cpu_info(self):
        cpu_info = [
            ("Núcleos físicos", psutil.cpu_count(logical=False)),
            ("Núcleos totales", psutil.cpu_count(logical=True)),
        ]

        cpufreq = psutil.cpu_freq()
        cpu_info.extend([
            ("Frecuencia máxima", f"{cpufreq.max:.2f}Mhz"),
            ("Frecuencia mínima", f"{cpufreq.min:.2f}Mhz"),
            ("Frecuencia actual", f"{cpufreq.current:.2f}Mhz")
        ])

        for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
            cpu_info.append((f"Uso de CPU en núcleo {i}", f"{percentage}%"))
        cpu_info.append(("Uso total de CPU", f"{psutil.cpu_percent()}%"))

        for item in cpu_info:
            self.system_info_tree.insert('', 'end', values=item)

    def get_memory_info(self):
        svmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        memory_info = [
            ("Memoria total", get_size(svmem.total)),
            ("Memoria disponible", get_size(svmem.available)),
            ("Memoria usada", get_size(svmem.used)),
            ("Porcentaje de memoria usada", f"{svmem.percent}%"),
            ("Swap total", get_size(swap.total)),
            ("Swap libre", get_size(swap.free)),
            ("Swap usado", get_size(swap.used)),
            ("Porcentaje de Swap usado", f"{swap.percent}%"),
        ]

        for item in memory_info:
            self.system_info_tree.insert('', 'end', values=item)

    def get_disk_info(self):
        disk_info = []
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_info.extend([
                    (f"Dispositivo: {partition.device}", ""),
                    ("  Punto de montaje", partition.mountpoint),
                    ("  Tipo de sistema de archivos", partition.fstype),
                    ("  Tamaño total", get_size(partition_usage.total)),
                    ("  Usado", get_size(partition_usage.used)),
                    ("  Libre", get_size(partition_usage.free)),
                    ("  Porcentaje usado", f"{partition_usage.percent}%"),
                ])
            except PermissionError:
                continue

        disk_io = psutil.disk_io_counters()
        disk_info.extend([
            ("Total leído", get_size(disk_io.read_bytes)),
            ("Total escrito", get_size(disk_io.write_bytes))
        ])

        for item in disk_info:
            self.system_info_tree.insert('', 'end', values=item)

    def get_network_info(self):
        net_info = []
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
                net_info.append((f"Interfaz: {interface_name}", ""))
                if str(address.family) == 'AddressFamily.AF_INET':
                    net_info.extend([
                        ("  Dirección IP", address.address),
                        ("  Máscara de red", address.netmask),
                        ("  IP de difusión", address.broadcast),
                    ])
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    net_info.extend([
                        ("  Dirección MAC", address.address),
                        ("  Máscara de red", address.netmask),
                        ("  MAC de difusión", address.broadcast),
                    ])

        net_io = psutil.net_io_counters()
        net_info.extend([
            ("Total bytes enviados", get_size(net_io.bytes_sent)),
            ("Total bytes recibidos", get_size(net_io.bytes_recv))
        ])

        for item in net_info:
            self.system_info_tree.insert('', 'end', values=item)

class FormularioGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Form")
        self.geometry("300x200")

        self.subForm1 = None
        self.subForm2 = None
        self.subForm3 = None
        self.subFormSubneteo = None
        self.subFormAnalizadorPC = None

        btn_abrir_1 = ttk.Button(self, text="Abrir Subneteo", command=lambda: self.lanzador(1))
        btn_abrir_1.pack(padx=20, pady=10)

        btn_abrir_2 = ttk.Button(self, text="Open SubForm 2", command=lambda: self.lanzador(2))
        btn_abrir_2.pack(padx=20, pady=10)

        btn_abrir_3 = ttk.Button(self, text="Open SubForm 3", command=lambda: self.lanzador(3))
        btn_abrir_3.pack(padx=20, pady=10)

        btn_abrir_4 = ttk.Button(self, text="Abrir Analizador de PC", command=lambda: self.lanzador(4))
        btn_abrir_4.pack(padx=20, pady=10)

        # Create a menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Create a menu
        menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Menu", menu=menu)

        menu.add_command(label="Abrir Subneteo", command=lambda: self.lanzador(1))
        menu.add_command(label="Open SubForm 2", command=lambda: self.lanzador(2))
        menu.add_command(label="Open SubForm 3", command=lambda: self.lanzador(3))
        menu.add_command(label="Abrir Analizador de PC", command=lambda: self.lanzador(4))

    def lanzador(self, ventana):
        if ventana == 1:
            if self.subFormSubneteo is None or not self.subFormSubneteo.winfo_exists():
                self.subFormSubneteo = SubFormularioSubneteo(self)
                self.subFormSubneteo.protocol("WM_DELETE_WINDOW", self.on_close_subform_subneteo)
            self.subFormSubneteo.deiconify()
        elif ventana == 2:
            if self.subForm2 is None or not self.subForm2.winfo_exists():
                self.subForm2 = SubFormulario2(self)
                self.subForm2.protocol("WM_DELETE_WINDOW", self.on_close_subform2)
            self.subForm2.deiconify()
        elif ventana == 3:
            if self.subForm3 is None or not self.subForm3.winfo_exists():
                self.subForm3 = SubFormulario3(self)
                self.subForm3.protocol("WM_DELETE_WINDOW", self.on_close_subform3)
            self.subForm3.deiconify()
        elif ventana == 4:
            if self.subFormAnalizadorPC is None or not self.subFormAnalizadorPC.winfo_exists():
                self.subFormAnalizadorPC = SubFormularioAnalizadorPC(self)
                self.subFormAnalizadorPC.protocol("WM_DELETE_WINDOW", self.on_close_subform_analizador_pc)
            self.subFormAnalizadorPC.deiconify()

    def on_close_subform2(self):
        self.subForm2.destroy()
        self.subForm2 = None

    def on_close_subform3(self):
        self.subForm3.destroy()
        self.subForm3 = None

    def on_close_subform_subneteo(self):
        self.subFormSubneteo.destroy()
        self.subFormSubneteo = None

    def on_close_subform_analizador_pc(self):
        self.subFormAnalizadorPC.destroy()
        self.subFormAnalizadorPC = None

if __name__ == "__main__":
    app = FormularioGUI()
    app.mainloop()
