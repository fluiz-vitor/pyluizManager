import subprocess
import os
import signal
import psutil
import json
import time
import threading
from typing import Dict, List, Optional


class XephyrInstance:

    def __init__(self, display_num: int, width: int = 800, height: int = 600, name: str = "", command: str = "", usb_port: str = ""):
        self.display_num = display_num
        self.width = width
        self.height = height
        self.name = name.strip() if name.strip() else f"Xephyr :{display_num}"
        self.command = command.strip()
        self.usb_port = usb_port.strip()
        self.process: Optional[subprocess.Popen] = None
        self.app_process: Optional[subprocess.Popen] = None
        self.is_running = False
        
    def start(self, width: int = None, height: int = None) -> bool:
        if self.is_running:
            return False
            
        # Usa as dimensões fornecidas ou as salvas na instância
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
            
        try:
            # Comando para iniciar o Xephyr
            cmd = [
                'Xephyr',
                f':{self.display_num}',
                '-ac',
                '-screen', f'{self.width}x{self.height}',
                '-host-cursor',
                '-title', self.name
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.is_running = True
            return True
            
        except Exception as e:
            print(f"Erro ao iniciar Xephyr :{self.display_num}: {e}")
            return False
    
    def _execute_command(self):
        try:
            # Aguarda o Xephyr inicializar completamente
            time.sleep(2)
            
            # Prepara o ambiente com o DISPLAY correto e porta USB
            env = os.environ.copy()
            env['DISPLAY'] = f':{self.display_num}'
            
            # Adiciona a porta USB se especificada
            if self.usb_port:
                env['ESP32_PORT'] = self.usb_port
                print(f"Usando porta USB {self.usb_port} para display :{self.display_num}")
            
            # Primeiro executa o xfwm4 (gerenciador de janelas)
            print(f"Iniciando xfwm4 no display :{self.display_num}")
            xfwm4_process = subprocess.Popen(
                ['xfwm4'],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            
            # Aguarda 2 segundos após xfwm4
            time.sleep(2)
            print(f"xfwm4 iniciado no display :{self.display_num}")
            
            # Se há comando(s) do usuário, processa um de cada vez
            if self.command:
                # Divide comandos por vírgula se houver múltiplos
                commands = [cmd.strip() for cmd in self.command.split(',') if cmd.strip()]
                
                for i, cmd in enumerate(commands):
                    if i > 0:  # Aguarda 2 segundos entre comandos (exceto o primeiro)
                        time.sleep(2)
                    
                    print(f"Executando comando '{cmd}' no display :{self.display_num}")
                    
                    # Executa o comando individual
                    self.app_process = subprocess.Popen(
                        f"bash -i -c '{cmd}'",
                        shell=True,
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setsid
                    )
                    
                    print(f"Comando '{cmd}' executado no display :{self.display_num}")
            
        except Exception as e:
            print(f"Erro ao executar comandos no display :{self.display_num}: {e}")
    
    def execute_commands(self):
        """Executa xfwm4 e comandos do usuário manualmente"""
        if self.is_running:
            print(f"Iniciando thread de comandos para display :{self.display_num}")
            threading.Thread(target=self._execute_command, daemon=True).start()
        else:
            print(f"Instância :{self.display_num} não está rodando, não pode executar comandos")
    
    def stop(self) -> bool:
        """Para a instância do Xephyr"""
        if not self.is_running or not self.process:
            return False
            
        try:
            # Para o aplicativo primeiro, se estiver rodando
            if self.app_process and self.app_process.poll() is None:
                try:
                    self.app_process.terminate()
                    self.app_process.wait(timeout=3)
                except:
                    try:
                        self.app_process.kill()
                    except:
                        pass
                self.app_process = None
            
            # Para o Xephyr
            self.process.terminate()
            self.process.wait(timeout=5)
            self.is_running = False
            self.process = None
            return True
            
        except subprocess.TimeoutExpired:
            # Se não terminou graciosamente, força o encerramento
            self.process.kill()
            self.process.wait()
            self.is_running = False
            self.process = None
            return True
            
        except Exception as e:
            print(f"Erro ao parar Xephyr :{self.display_num}: {e}")
            return False
    
    def is_alive(self) -> bool:
        """Verifica se a instância ainda está rodando"""
        if not self.process:
            self.is_running = False
            return False
            
        poll = self.process.poll()
        if poll is not None:
            self.is_running = False
            return False
            
        return True


class XephyrManager:
    """Gerenciador principal das instâncias Xephyr"""
    
    def __init__(self, config_file: str = "xephyr_config.json"):
        self.instances: Dict[int, XephyrInstance] = {}
        self.config_file = config_file
        self.last_width = 800
        self.last_height = 600
        self.load_config()
        
    def _find_available_display(self) -> int:
        """Encontra o menor número de display disponível"""
        display_num = 1
        while display_num in self.instances or self._display_in_use(display_num):
            display_num += 1
        return display_num
    
    def _display_in_use(self, display_num: int) -> bool:
        """Verifica se um display já está em uso pelo sistema"""
        try:
            # Verifica se existe um socket X para esse display
            socket_path = f"/tmp/.X11-unix/X{display_num}"
            return os.path.exists(socket_path)
        except:
            return False
    
    def create_instance(self, width: int = 800, height: int = 600, name: str = "", command: str = "", usb_port: str = "") -> Optional[int]:
        """Cria uma nova instância do Xephyr (sem iniciar)"""
        # Valida se o nome foi fornecido
        if not name.strip():
            print("Erro: Nome da instância é obrigatório")
            return None
            
        display_num = self._find_available_display()
        
        # Salva as últimas dimensões usadas
        self.last_width = width
        self.last_height = height
        
        # Cria a instância mas NÃO inicia o Xephyr
        instance = XephyrInstance(display_num, width, height, name, command, usb_port)
        self.instances[display_num] = instance
        self.save_config()
        
        return display_num
    
    def stop_instance(self, display_num: int) -> bool:
        """Para uma instância específica"""
        if display_num not in self.instances:
            return False
            
        return self.instances[display_num].stop()
    
    def remove_instance(self, display_num: int) -> bool:
        """Remove uma instância (para antes de remover)"""
        if display_num not in self.instances:
            return False
            
        instance = self.instances[display_num]
        if instance.is_running:
            instance.stop()
            
        del self.instances[display_num]
        self.save_config()
        return True
    
    def get_instances(self) -> List[Dict]:
        """Retorna lista com informações de todas as instâncias"""
        instances_info = []
        
        for display_num, instance in self.instances.items():
            # Atualiza o status da instância
            is_alive = instance.is_alive()
            
            instances_info.append({
                'display': display_num,
                'running': is_alive,
                'pid': instance.process.pid if instance.process and is_alive else None,
                'width': instance.width,
                'height': instance.height,
                'name': instance.name,
                'command': instance.command,
                'usb_port': instance.usb_port
            })
            
        return instances_info
    
    def cleanup_dead_instances(self):
        """Remove instâncias que não estão mais rodando"""
        dead_instances = []
        
        for display_num, instance in self.instances.items():
            if not instance.is_alive():
                dead_instances.append(display_num)
        
        for display_num in dead_instances:
            del self.instances[display_num]
        
        if dead_instances:
            self.save_config()
    
    def shutdown_all(self):
        """Para todas as instâncias mas mantém os dados salvos"""
        for instance in self.instances.values():
            if instance.is_running:
                instance.stop()
        
        # NÃO limpa as instâncias, apenas para os processos
        self.save_config()
    
    def save_config(self):
        """Salva as configurações em arquivo JSON"""
        try:
            config_data = {
                'last_width': self.last_width,
                'last_height': self.last_height,
                'instances': {}
            }
            
            # Salva informações das instâncias (não salva processos ativos)
            for display_num, instance in self.instances.items():
                config_data['instances'][str(display_num)] = {
                    'display_num': instance.display_num,
                    'width': instance.width,
                    'height': instance.height,
                    'name': instance.name,
                    'command': instance.command,
                    'usb_port': instance.usb_port
                }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def load_config(self):
        """Carrega as configurações do arquivo JSON"""
        try:
            if not os.path.exists(self.config_file):
                return
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Restaura as últimas dimensões usadas
            self.last_width = config_data.get('last_width', 800)
            self.last_height = config_data.get('last_height', 600)
            
            # Restaura as instâncias (mas não as inicia automaticamente)
            instances_data = config_data.get('instances', {})
            for display_str, instance_data in instances_data.items():
                display_num = int(display_str)
                instance = XephyrInstance(
                    display_num=instance_data['display_num'],
                    width=instance_data['width'],
                    height=instance_data['height'],
                    name=instance_data.get('name', f"Xephyr :{display_num}"),
                    command=instance_data.get('command', ""),
                    usb_port=instance_data.get('usb_port', "")
                )
                self.instances[display_num] = instance
                
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def get_last_dimensions(self) -> tuple:
        """Retorna as últimas dimensões usadas"""
        return (self.last_width, self.last_height)
    
    def update_instance(self, display_num: int, name: str, command: str, width: int, height: int, usb_port: str = "") -> bool:
        """Atualiza os dados de uma instância existente"""
        if display_num not in self.instances:
            return False
        
        instance = self.instances[display_num]
        
        # Atualiza os dados da instância
        instance.name = name
        instance.command = command
        instance.width = width
        instance.height = height
        instance.usb_port = usb_port
        
        # Salva as configurações
        self.save_config()
        
        return True
    
    def get_available_usb_ports(self) -> List[str]:
        """Retorna lista de portas USB disponíveis"""
        try:
            import glob
            # Busca por dispositivos ttyUSB (Linux)
            usb_ports = glob.glob('/dev/ttyUSB*')
            # Busca por dispositivos ttyACM (Arduino/ESP32)
            acm_ports = glob.glob('/dev/ttyACM*')
            return sorted(usb_ports + acm_ports)
        except:
            return []


if __name__ == "__main__":
    # Teste básico
    manager = XephyrManager()
    
    print("Testando gerenciador Xephyr...")
    
    # Cria uma instância
    display = manager.create_instance()
    if display:
        print(f"Instância criada no display :{display}")
        
        input("Pressione Enter para parar a instância...")
        
        manager.stop_instance(display)
        print(f"Instância :{display} parada")
        
        manager.remove_instance(display)
        print(f"Instância :{display} removida")
    else:
        print("Falha ao criar instância")
