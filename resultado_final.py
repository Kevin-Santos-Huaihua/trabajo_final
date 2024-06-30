import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress
import psutil
import platform
from datetime import datetime
import sqlite3
import requests

# Función para representar tamaños en bits.
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

# Función para crear la base de datos SQLite y las tablas
def crear_base_datos():
    try:
        conn = sqlite3.connect('mi_base_datos.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS breaches (
            id TEXT PRIMARY KEY,
            name TEXT,
            title TEXT,
            domain TEXT,
            breach_date TEXT,
            description TEXT
        )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error al crear la base de datos: {e}")
    finally:
        conn.close()

import tkinter as tk
from tkinter import filedialog

class SubFormularioLogViewer(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Log Viewer")
        self.geometry("700x450")
        self.create_widgets()

    def create_widgets(self):
        # Widget para cargar archivo de log
        tk.Label(self, text="Cargar archivo de log:").grid(row=0, column=0, padx=10, pady=10)
        self.log_file_entry = tk.Entry(self, width=50)
        self.log_file_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self, text="Buscar", command=self.buscar_archivo).grid(row=0, column=2, padx=10, pady=10)

        # Widget para filtrar entradas de log
        tk.Label(self, text="Filtrar por:").grid(row=1, column=0, padx=10, pady=10)
        self.filter_by_label = tk.Label(self, text="Fecha:")
        self.filter_by_label.grid(row=1, column=1, padx=10, pady=10)
        self.filter_by_date_entry = tk.Entry(self, width=20)
        self.filter_by_date_entry.grid(row=1, column=2, padx=10, pady=10)
        self.filter_by_severity_label = tk.Label(self, text="Nivel de severidad:")
        self.filter_by_severity_label.grid(row=2, column=1, padx=10, pady=10)
        self.filter_by_severity_entry = tk.Entry(self, width=20)
        self.filter_by_severity_entry.grid(row=2, column=2, padx=10, pady=10)
        self.filter_by_origin_label = tk.Label(self, text="Origen:")
        self.filter_by_origin_label.grid(row=3, column=1, padx=10, pady=10)
        self.filter_by_origin_entry = tk.Entry(self, width=20)
        self.filter_by_origin_entry.grid(row=3, column=2, padx=10, pady=10)
        tk.Button(self, text="Filtrar", command=self.filtrar_log_entries).grid(row=4, column=1, columnspan=2, padx=10, pady=10)

        # Widget para mostrar estadísticas
        tk.Label(self, text="Estadísticas:").grid(row=5, column=0, padx=10, pady=10)
        self.stats_text = tk.Text(self, height=10, width=50)
        self.stats_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

    def buscar_archivo(self):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo de log", filetypes=[("Log files", "*.log")])
        if file_path:
            self.log_file_entry.delete(0, tk.END)
            self.log_file_entry.insert(0, file_path)
            self.cargar_log_file()

    def cargar_log_file(self):
        log_file_path = self.log_file_entry.get()
        if log_file_path:
            with open(log_file_path, 'r') as f:
                log_entries = [line.strip() for line in f.readlines()]
            self.log_entries = log_entries
            self.mostrar_estadisticas()

    def filtrar_log_entries(self):
        filter_by_date = self.filter_by_date_entry.get()
        filter_by_severity = self.filter_by_severity_entry.get()
        filter_by_origin = self.filter_by_origin_entry.get()
        filtered_log_entries = []
        for log_entry in self.log_entries:
            if filter_by_date and filter_by_date not in log_entry:
                continue
            if filter_by_severity and filter_by_severity not in log_entry:
                continue
            if filter_by_origin and filter_by_origin not in log_entry:
                continue
            filtered_log_entries.append(log_entry)
        self.log_entries = filtered_log_entries
        self.mostrar_estadisticas()

    def mostrar_estadisticas(self):
        stats = {}
        for log_entry in self.log_entries:
            severity = log_entry.split(':')[0]
            origin = log_entry.split(':')[1]
            if severity not in stats:
                stats[severity] = {'count': 0, 'origins': {}}
            stats[severity]['count'] += 1
            if origin not in stats[severity]['origins']:
                stats[severity]['origins'][origin] = 0
            stats[severity]['origins'][origin] += 1
        stats_text = ""
        for severity, severity_stats in stats.items():
            stats_text += f"{severity}: {severity_stats['count']} entradas\n"
            for origin, count in severity_stats['origins'].items():
                stats_text +=f"  {origin}: {count} entradas\n"
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, stats_text)

class SubFormularioTrabajoAPI(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Trabajo con API")
        self.create_widgets()
        self.crear_base_datos()

    def create_widgets(self):
        tk.Button(self, text="Extraer Datos API", command=self.extraer_datos_api).pack(padx=20, pady=5)
        tk.Button(self, text="Insertar Datos", command=self.insertar_datos_bd).pack(padx=20, pady=5)
        tk.Button(self, text="Modificar Datos", command=self.modificar_datos_bd).pack(padx=20, pady=5)
        tk.Button(self, text="Eliminar Datos", command=self.eliminar_datos_bd).pack(padx=20, pady=5)
        tk.Button(self, text="Mostrar Datos", command=self.mostrar_datos_almacenados).pack(padx=20, pady=5)

        columns = ("ID", "Nombre", "Título", "Dominio", "Fecha del Breach", "Descripción")
        self.table = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.table.heading(col, text=col)
        self.table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def crear_base_datos(self):
        conn = sqlite3.connect('mi_base_datos.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS breaches (
                id TEXT PRIMARY KEY,
                name TEXT,
                title TEXT,
                domain TEXT,
                breach_date TEXT,
                description TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def extraer_datos_api(self):
        api_url = "https://haveibeenpwned.com/api/v3/breaches"
        headers = {
            'hibp-api-key': 'YOUR_HIBP_API_KEY',
            'User-Agent': 'Python script'
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            breaches_data = response.json()

            with sqlite3.connect('mi_base_datos.db') as conn:
                cursor = conn.cursor()
                for breach in breaches_data:
                    breach_id = breach.get('Name')
                    name = breach.get('Name')
                    title = breach.get('Title')
                    domain = breach.get('Domain')
                    breach_date = breach.get('BreachDate')
                    description = breach.get('Description')

                    cursor.execute('''
                    INSERT OR REPLACE INTO breaches (id, name, title, domain, breach_date, description)
                    VALUES (?,?,?,?,?,?)
                    ''', (breach_id, name, title, domain, breach_date, description))

                conn.commit()
            self.mostrar_datos_almacenados()
            messagebox.showinfo("Éxito", "Datos extraídos y almacenados exitosamente en la base de datos.")
        except requests.exceptions.HTTPError as http_err:
            messagebox.showerror("Error HTTP", f"Error HTTP: {http_err}")
        except Exception as err:
            messagebox.showerror("Error", f"Error: {err}")

    def insertar_datos_bd(self):
        def insert():
            try:
                with sqlite3.connect('mi_base_datos.db') as conn:
                    cursor = conn.cursor()

                    cursor.execute('''
                    INSERT INTO breaches (id, name, title, domain, breach_date, description)
                    VALUES (?,?,?,?,?,?)
                    ''', (entry_id.get(), entry_name.get(), entry_title.get(), entry_domain.get(), entry_breach_date.get(), entry_description.get()))

                    conn.commit()
                self.mostrar_datos_almacenados()
                messagebox.showinfo("Éxito", "Datos insertados exitosamente en la base de datos.")
                insert_window.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al insertar datos: {e}")

        insert_window = tk.Toplevel(self)
        insert_window.title("Insertar Datos")

        tk.Label(insert_window, text="ID:").grid(row=0, column=0, padx=10, pady=5)
        entry_id = tk.Entry(insert_window)
        entry_id.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(insert_window, text="Nombre:").grid(row=1, column=0, padx=10, pady=5)
        entry_name = tk.Entry(insert_window)
        entry_name.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(insert_window, text="Título:").grid(row=2, column=0, padx=10, pady=5)
        entry_title = tk.Entry(insert_window)
        entry_title.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(insert_window, text="Dominio:").grid(row=3, column=0, padx=10, pady=5)
        entry_domain = tk.Entry(insert_window)
        entry_domain.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(insert_window, text="Fecha del Breach:").grid(row=4, column=0, padx=10, pady=5)
        entry_breach_date = tk.Entry(insert_window)
        entry_breach_date.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(insert_window, text="Descripción:").grid(row=5, column=0, padx=10, pady=5)
        entry_description = tk.Entry(insert_window)
        entry_description.grid(row=5, column=1, padx=10, pady=5)

        tk.Button(insert_window, text="Insertar", command=insert).grid(row=6, columnspan=2, padx=10, pady=10)

    def modificar_datos_bd(self):
        def update():
            try:
                with sqlite3.connect('mi_base_datos.db') as conn:
                    cursor = conn.cursor()

                    if entry_name.get():
                        cursor.execute('UPDATE breaches SET name =? WHERE id =?', (entry_name.get(), entry_id.get()))
                    if entry_title.get():
                        cursor.execute('UPDATE breaches SET title =? WHERE id =?', (entry_title.get(), entry_id.get()))
                    if entry_domain.get():
                        cursor.execute('UPDATE breaches SET domain =? WHERE id =?', (entry_domain.get(), entry_id.get()))
                    if entry_breach_date.get():
                        cursor.execute('UPDATE breaches SET breach_date =? WHERE id =?', (entry_breach_date.get(), entry_id.get()))
                    if entry_description.get():
                        cursor.execute('UPDATE breaches SET description =? WHERE id =?', (entry_description.get(), entry_id.get()))

                    conn.commit()
                self.mostrar_datos_almacenados()
                messagebox.showinfo("Éxito", "Datos modificados exitosamente en la base de datos.")
                update_window.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al modificar datos: {e}")

        update_window = tk.Toplevel(self)
        update_window.title("Modificar Datos")

        tk.Label(update_window, text="ID:").grid(row=0, column=0, padx=10, pady=5)
        entry_id = tk.Entry(update_window)
        entry_id.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(update_window, text="Nuevo Nombre:").grid(row=1, column=0, padx=10, pady=5)
        entry_name = tk.Entry(update_window)
        entry_name.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(update_window, text="Nuevo Título:").grid(row=2, column=0, padx=10, pady=5)
        entry_title = tk.Entry(update_window)
        entry_title.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(update_window, text="Nuevo Dominio:").grid(row=3, column=0, padx=10, pady=5)
        entry_domain = tk.Entry(update_window)
        entry_domain.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(update_window, text="Nueva Fecha del Breach:").grid(row=4, column=0, padx=10, pady=5)
        entry_breach_date = tk.Entry(update_window)
        entry_breach_date.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(update_window, text="Nueva Descripción:").grid(row=5, column=0, padx=10, pady=5)
        entry_description = tk.Entry(update_window)
        entry_description.grid(row=5, column=1, padx=10, pady=5)

        tk.Button(update_window, text="Modificar", command=update).grid(row=6, columnspan=2, padx=10, pady=10)

    def eliminar_datos_bd(self):
        def delete():
            try:
                with sqlite3.connect('mi_base_datos.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM breaches WHERE id =?', (entry_id.get(),))

                    conn.commit()
                self.mostrar_datos_almacenados()
                messagebox.showinfo("Éxito", "Datos eliminados exitosamente de la base de datos.")
                delete_window.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al eliminar datos: {e}")

        delete_window = tk.Toplevel(self)
        delete_window.title("Eliminar Datos")

        tk.Label(delete_window, text="ID:").grid(row=0, column=0, padx=10, pady=5)
        entry_id = tk.Entry(delete_window)
        entry_id.grid(row=0, column=1, padx=10, pady=5)

        tk.Button(delete_window, text="Eliminar", command=delete).grid(row=1, columnspan=2, padx=10, pady=10)

    def mostrar_datos_almacenados(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            with sqlite3.connect('mi_base_datos.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM breaches')
                rows = cursor.fetchall()

                for row in rows:
                    self.table.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al mostrar datos: {e}")


class SubFormularioCalculadoraSubred(tk.Toplevel):
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

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicación Principal")
        self.geometry("300x200")
        self.create_widgets()

    def create_widgets(self):

        tk.Button(self, text="Calculadora de Subredes", command=self.open_subformulario_calculadora_subred).pack(padx=20, pady=10)
        tk.Button(self, text="Log Viewer", command=self.open_SubFormulario_LogViewer).pack(padx=20, pady=10)
        tk.Button(self, text="Trabajo con API", command=self.open_subformulario_trabajo_api).pack(padx=20, pady=10)
        tk.Button(self, text="Analizador de PC", command=self.open_subformulario_analizador_pc).pack(padx=20, pady=10)

    def open_SubFormulario_LogViewer(self):
        SubFormularioLogViewer(self)

    def open_subformulario_trabajo_api(self):
        SubFormularioTrabajoAPI(self)

    def open_subformulario_calculadora_subred(self):
        SubFormularioCalculadoraSubred(self)

    def open_subformulario_analizador_pc(self):
        SubFormularioAnalizadorPC(self)

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
