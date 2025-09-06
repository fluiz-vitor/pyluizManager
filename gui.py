import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from xephyr_manager import XephyrManager

class XephyrGUI:
    def __init__(self):
        self.manager = XephyrManager()
        self.root = tk.Tk()
        self.setup_window()
        self.setup_widgets()
        self.load_last_dimensions()
        self.update_thread_running = True
        self.start_update_thread()
        
    def setup_window(self):
        self.root.title("Gerenciador de Instâncias Xephyr")
        self.root.geometry("950x500")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        style = ttk.Style()
        style.theme_use('clam')
        
    def setup_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)  # O frame principal das instâncias está na row 1
        
        # Título
        title_label = ttk.Label(
            main_frame, 
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Botão para criar nova instância
        self.create_button = ttk.Button(
            controls_frame,

            text="Nova Instância",
            command=self.create_instance,
            style="Accent.TButton"
        )
        self.create_button.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Frame para configurações
        config_frame = ttk.Frame(controls_frame)
        config_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        config_frame.columnconfigure(1, weight=1)
        
        # Campo para nome
        ttk.Label(config_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar(value="")
        name_entry = ttk.Entry(config_frame, textvariable=self.name_var, width=20)
        name_entry.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Campo para comando/aplicativo
        ttk.Label(config_frame, text="Comando:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.command_var = tk.StringVar(value="")
        command_entry = ttk.Entry(config_frame, textvariable=self.command_var, width=20)
        command_entry.grid(row=1, column=1, padx=(5, 0), sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Campo para porta USB
        ttk.Label(config_frame, text="Porta USB:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.usb_port_var = tk.StringVar(value="")
        
        # Frame para porta USB com botão de refresh
        usb_frame = ttk.Frame(config_frame)
        usb_frame.grid(row=2, column=1, padx=(5, 0), sticky=(tk.W, tk.E), pady=(5, 0))
        
        usb_entry = ttk.Entry(usb_frame, textvariable=self.usb_port_var, width=15)
        usb_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        refresh_button = ttk.Button(usb_frame, text="🔍", width=3, command=self.refresh_usb_ports)
        refresh_button.grid(row=0, column=1, padx=(5, 0))
        
        usb_frame.columnconfigure(0, weight=1)
        
        # Frame para dimensões
        dimensions_frame = ttk.Frame(config_frame)
        dimensions_frame.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(dimensions_frame, text="Largura:").grid(row=0, column=0, sticky=tk.W)
        self.width_var = tk.StringVar(value="800")
        width_entry = ttk.Entry(dimensions_frame, textvariable=self.width_var, width=8)
        width_entry.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(dimensions_frame, text="Altura:").grid(row=0, column=2, sticky=tk.W)
        self.height_var = tk.StringVar(value="600")
        height_entry = ttk.Entry(dimensions_frame, textvariable=self.height_var, width=8)
        height_entry.grid(row=0, column=3, padx=5)
        
        # Botão para parar todas
        self.stop_all_button = ttk.Button(
            controls_frame,
            text="Parar Todas",
            command=self.stop_all_instances
        )
        self.stop_all_button.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Botão para limpar instâncias mortas
        self.cleanup_button = ttk.Button(
            controls_frame,
            text="Limpar Mortas",
            command=self.cleanup_dead_instances
        )
        self.cleanup_button.grid(row=3, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Frame principal das instâncias (contém ações e lista)
        instances_main_frame = ttk.LabelFrame(main_frame, text="Gerenciamento de Instâncias", padding="10")
        instances_main_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        instances_main_frame.columnconfigure(0, weight=1)
        instances_main_frame.rowconfigure(1, weight=1)  # Lista expandirá
        
        # Frame de ações dentro do frame principal
        actions_frame = ttk.Frame(instances_main_frame)
        actions_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(actions_frame, text="Ações da Instância Selecionada:", font=('', 9, 'bold')).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 5))
        
        self.start_button = ttk.Button(
            actions_frame,
            text="Iniciar",
            command=self.start_selected_instance,
            state=tk.DISABLED
        )
        self.start_button.grid(row=1, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(
            actions_frame,
            text="Parar",
            command=self.stop_selected_instance,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=1, column=1, padx=5)
        
        self.remove_button = ttk.Button(
            actions_frame,
            text="Remover",
            command=self.remove_selected_instance,
            state=tk.DISABLED
        )
        self.remove_button.grid(row=1, column=2, padx=5)
        
        self.execute_button = ttk.Button(
            actions_frame,
            text="Executar Comando",
            command=self.execute_command_in_instance,
            state=tk.DISABLED
        )
        self.execute_button.grid(row=1, column=3, padx=(5, 0))
        
        # Frame da lista de instâncias dentro do frame principal
        list_frame = ttk.Frame(instances_main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)  # Row 1 porque row 0 tem o label
        
        ttk.Label(list_frame, text="Lista de Instâncias:", font=('', 9, 'bold')).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Treeview para listar instâncias
        columns = ('Nome', 'Display', 'Status', 'Resolução', 'Comando', 'USB')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configura as colunas
        self.tree.heading('Nome', text='Nome')
        self.tree.heading('Display', text='Display')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Resolução', text='Resolução')
        self.tree.heading('Comando', text='Comando')
        self.tree.heading('USB', text='USB')
        
        self.tree.column('Nome', width=120, anchor=tk.W)
        self.tree.column('Display', width=60, anchor=tk.CENTER)
        self.tree.column('Status', width=60, anchor=tk.CENTER)
        self.tree.column('Resolução', width=80, anchor=tk.CENTER)
        self.tree.column('Comando', width=100, anchor=tk.W)
        self.tree.column('USB', width=80, anchor=tk.W)
        
        # Scrollbar para o treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        

        
        # Bind para seleção no treeview
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_double_click_edit)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def create_instance(self):
        """Cria uma nova instância do Xephyr"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            name = self.name_var.get().strip()
            command = self.command_var.get().strip()
            usb_port = self.usb_port_var.get().strip()
            
            if width <= 0 or height <= 0:
                raise ValueError("Dimensões devem ser positivas")
            
            # Verifica se o nome foi informado
            if not name:
                messagebox.showerror("Erro", "É obrigatório informar um nome para a instância!")
                return
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Dimensões inválidas: {e}")
            return
            
        # Executa em thread para não bloquear a GUI
        def create_thread():
            display = self.manager.create_instance(width, height, name, command, usb_port)
            if display:
                command_info = f" com comando '{command}'" if command else ""
                usb_info = f" e porta USB '{usb_port}'" if usb_port else ""
                self.status_var.set(f"Instância '{name}' criada no display :{display}{command_info}{usb_info}")
                # Limpa os campos para a próxima instância
                self.root.after(0, lambda: (self.name_var.set(""), self.command_var.set(""), self.usb_port_var.set("")))
            else:
                self.status_var.set("Falha ao criar instância")
                messagebox.showerror("Erro", "Não foi possível criar a instância")
        
        threading.Thread(target=create_thread, daemon=True).start()
    
    def stop_all_instances(self):
        """Para todas as instâncias ativas"""
        if messagebox.askyesno("Confirmar", "Deseja parar todas as instâncias?"):
            # Para as instâncias mas mantém os dados salvos
            for instance in self.manager.instances.values():
                if instance.is_running:
                    instance.stop()
            self.manager.save_config()
            self.status_var.set("Todas as instâncias foram paradas")
    
    def cleanup_dead_instances(self):
        """Remove instâncias que não estão mais rodando"""
        self.manager.cleanup_dead_instances()
        self.status_var.set("Instâncias mortas removidas")
    
    def on_tree_select(self, event):
        """Chamado quando uma linha é selecionada no treeview"""
        selection = self.tree.selection()
        if selection:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.remove_button.config(state=tk.NORMAL)
            self.execute_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            self.remove_button.config(state=tk.DISABLED)
            self.execute_button.config(state=tk.DISABLED)
    
    def get_selected_display(self):
        """Retorna o número do display da instância selecionada"""
        selection = self.tree.selection()
        if not selection:
            return None
            
        item = self.tree.item(selection[0])
        display_text = item['values'][1]  # Display agora está na coluna 1
        return int(display_text.replace(':', ''))
    
    def start_selected_instance(self):
        """Inicia a instância selecionada"""
        display = self.get_selected_display()
        if display is None:
            return
            
        try:
            instance = self.manager.instances.get(display)
            if instance and not instance.is_running:
                print(f"Iniciando instância :{display}")
                if instance.start():
                    print(f"Xephyr iniciado, executando comandos para :{display}")
                    # Executa os comandos após iniciar
                    instance.execute_commands()
                    self.status_var.set(f"Instância :{display} iniciada com comandos")
                else:
                    self.status_var.set(f"Falha ao iniciar instância :{display}")
            else:
                self.status_var.set(f"Instância :{display} já está rodando")
                
        except Exception as e:
            print(f"Erro ao iniciar instância :{display}: {e}")
            messagebox.showerror("Erro", f"Erro ao iniciar instância: {e}")
    
    def stop_selected_instance(self):
        """Para a instância selecionada"""
        display = self.get_selected_display()
        if display is None:
            return
            
        if self.manager.stop_instance(display):
            self.status_var.set(f"Instância :{display} parada")
        else:
            self.status_var.set(f"Falha ao parar instância :{display}")
    
    def remove_selected_instance(self):
        """Remove a instância selecionada"""
        display = self.get_selected_display()
        if display is None:
            return
            
        if messagebox.askyesno("Confirmar", f"Deseja remover a instância :{display}?"):
            if self.manager.remove_instance(display):
                self.status_var.set(f"Instância :{display} removida")
            else:
                self.status_var.set(f"Falha ao remover instância :{display}")
    
    def execute_command_in_instance(self):
        """Executa um comando na instância selecionada"""
        display = self.get_selected_display()
        if display is None:
            return
        
        # Solicita o comando ao usuário
        command = simpledialog.askstring(
            "Executar Comando",
            f"Digite o comando para executar no display :{display}:",
            initialvalue=""
        )
        
        if command and command.strip():
            # Mostra mensagem imediata
            self.status_var.set(f"Aguardando 2s para executar '{command.strip()}' no display :{display}...")
            
            # Executa em thread para não bloquear a GUI
            def execute_thread():
                try:
                    import subprocess
                    import os
                    import time
                    
                    # Aguarda 2 segundos antes de executar o comando
                    time.sleep(2)
                    
                    # Prepara o ambiente com o DISPLAY correto
                    env = os.environ.copy()
                    env['DISPLAY'] = f':{display}'
                    
                    # Verifica se xfwm4 já está rodando, se não, inicia
                    try:
                        # Tenta verificar se xfwm4 já está rodando
                        check_cmd = f"DISPLAY=:{display} pgrep -f xfwm4"
                        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, env=env)
                        
                        if result.returncode != 0:  # xfwm4 não está rodando
                            # Inicia xfwm4
                            subprocess.Popen(
                                ['xfwm4'],
                                env=env,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                preexec_fn=os.setsid
                            )
                            time.sleep(2)  # Aguarda xfwm4 inicializar
                    except:
                        pass  # Se falhar, continua sem o xfwm4
                    
                    # Processa comandos separados por vírgula
                    commands = [cmd.strip() for cmd in command.strip().split(',') if cmd.strip()]
                    
                    for i, cmd in enumerate(commands):
                        if i > 0:  # Aguarda 2 segundos entre comandos
                            time.sleep(2)
                        
                        # Executa o comando usando bash para resolver aliases
                        subprocess.Popen(
                            f"bash -i -c '{cmd}'",
                            shell=True,
                            env=env,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            preexec_fn=os.setsid
                        )
                    
                    self.status_var.set(f"Comando '{command.strip()}' executado no display :{display}")
                    
                except Exception as e:
                    self.status_var.set(f"Erro ao executar comando: {e}")
            
            threading.Thread(target=execute_thread, daemon=True).start()
    
    def on_double_click_edit(self, event):
        """Chamado quando uma instância é clicada duas vezes para edição"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Obtém os dados da instância selecionada
        item = self.tree.item(selection[0])
        values = item['values']
        
        if not values:
            return
        
        # Extrai os dados da instância
        name = values[0]
        display_text = values[1]
        display_num = int(display_text.replace(':', ''))
        resolution = values[3]
        command = values[4] if values[4] != "-" else ""
        usb_port = values[5] if values[5] != "-" else ""
        
        # Extrai largura e altura da resolução
        width, height = resolution.split('x')
        
        # Cria janela de edição
        self.create_edit_window(display_num, name, command, int(width), int(height), usb_port)
    
    def create_edit_window(self, display_num, current_name, current_command, current_width, current_height, current_usb_port=""):
        """Cria janela para editar instância"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Editar Instância :{display_num}")
        edit_window.geometry("400x350")
        edit_window.resizable(False, False)
        edit_window.transient(self.root)
        
        # Centraliza a janela
        edit_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Aguarda a janela estar pronta antes de definir grab_set
        edit_window.update_idletasks()
        edit_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(edit_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text=f"Editar Instância :{display_num}", font=('', 12, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Campo Nome
        ttk.Label(main_frame, text="Nome:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=current_name)
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=30)
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Campo Comando
        ttk.Label(main_frame, text="Comando:").grid(row=2, column=0, sticky=tk.W, pady=5)
        command_var = tk.StringVar(value=current_command)
        command_entry = ttk.Entry(main_frame, textvariable=command_var, width=30)
        command_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Campo Porta USB
        ttk.Label(main_frame, text="Porta USB:").grid(row=3, column=0, sticky=tk.W, pady=5)
        usb_var = tk.StringVar(value=current_usb_port)
        usb_entry = ttk.Entry(main_frame, textvariable=usb_var, width=30)
        usb_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Frame para dimensões
        dimensions_frame = ttk.Frame(main_frame)
        dimensions_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(dimensions_frame, text="Largura:").grid(row=0, column=0, sticky=tk.W)
        width_var = tk.StringVar(value=str(current_width))
        width_entry = ttk.Entry(dimensions_frame, textvariable=width_var, width=8)
        width_entry.grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(dimensions_frame, text="Altura:").grid(row=0, column=2, sticky=tk.W)
        height_var = tk.StringVar(value=str(current_height))
        height_entry = ttk.Entry(dimensions_frame, textvariable=height_var, width=8)
        height_entry.grid(row=0, column=3, padx=5)
        
        # Frame para botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        def save_changes():
            try:
                # Validações
                new_name = name_var.get().strip()
                if not new_name:
                    messagebox.showerror("Erro", "Nome é obrigatório!")
                    return
                
                new_width = int(width_var.get())
                new_height = int(height_var.get())
                if new_width <= 0 or new_height <= 0:
                    messagebox.showerror("Erro", "Dimensões devem ser positivas!")
                    return
                
                new_command = command_var.get().strip()
                new_usb_port = usb_var.get().strip()
                
                # Atualiza a instância no gerenciador
                if self.manager.update_instance(display_num, new_name, new_command, new_width, new_height, new_usb_port):
                    self.status_var.set(f"Instância :{display_num} atualizada")
                    edit_window.destroy()
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar instância")
                    
            except ValueError:
                messagebox.showerror("Erro", "Dimensões devem ser números válidos!")
        
        def cancel_edit():
            edit_window.destroy()
        
        # Botões
        save_button = ttk.Button(buttons_frame, text="Salvar", command=save_changes)
        save_button.grid(row=0, column=0, padx=(0, 10))
        
        cancel_button = ttk.Button(buttons_frame, text="Cancelar", command=cancel_edit)
        cancel_button.grid(row=0, column=1, padx=(10, 0))
        
        # Configura o grid
        edit_window.columnconfigure(0, weight=1)
        edit_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Foca no primeiro campo
        name_entry.focus_set()
    
    def refresh_usb_ports(self):
        try:
            ports = self.manager.get_available_usb_ports()
            if ports:
                # Mostra as portas disponíveis em uma janela
                port_list = "\n".join(ports)
                messagebox.showinfo("Portas USB Disponíveis", f"Portas encontradas:\n\n{port_list}")
            else:
                messagebox.showinfo("Portas USB", "Nenhuma porta USB encontrada.\n\nCertifique-se de que:\n- ESP32 está conectado\n- Permissões USB estão corretas\n- Dispositivo aparece em /dev/ttyUSB* ou /dev/ttyACM*")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar portas USB: {e}")
    
    def update_instances_list(self):
        """Atualiza a lista de instâncias na interface"""
        # Preserva a seleção atual
        selected_items = self.tree.selection()
        selected_displays = []
        for item in selected_items:
            values = self.tree.item(item)['values']
            if values:
                selected_displays.append(values[1])  # Display está na coluna 1
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        instances = self.manager.get_instances()
        for instance in instances:
            name = instance['name']
            display = f":{instance['display']}"
            status = "Rodando" if instance['running'] else "Parada"
            resolution = f"{instance['width']}x{instance['height']}"
            command = instance['command'] if instance['command'] else "-"
            usb_port = instance['usb_port'] if instance['usb_port'] else "-"
            
            tags = ('running',) if instance['running'] else ('stopped',)
            
            item = self.tree.insert('', tk.END, values=(name, display, status, resolution, command, usb_port), tags=tags)
            
            if display in selected_displays:
                self.tree.selection_add(item)
        
        self.tree.tag_configure('running', foreground='green')
        self.tree.tag_configure('stopped', foreground='red')
    
    def load_last_dimensions(self):
        last_width, last_height = self.manager.get_last_dimensions()
        self.width_var.set(str(last_width))
        self.height_var.set(str(last_height))
    
    def start_update_thread(self):
        def update_loop():
            while self.update_thread_running:
                try:
                    self.root.after(0, self.update_instances_list)
                    time.sleep(3)  # Atualiza a cada 3 segundos
                except:
                    break
        
        threading.Thread(target=update_loop, daemon=True).start()
    
    def on_closing(self):
        if messagebox.askyesno("Sair", "Deseja parar todas as instâncias antes de sair?"):
            # Para as instâncias mas mantém os dados salvos
            for instance in self.manager.instances.values():
                if instance.is_running:
                    instance.stop()
            # Salva as configurações antes de sair
            self.manager.save_config()
        
        self.update_thread_running = False
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()


def main():
    try:
        app = XephyrGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nEncerrando aplicação...")
    except Exception as e:
        print(f"Erro na aplicação: {e}")


if __name__ == "__main__":
    main()
