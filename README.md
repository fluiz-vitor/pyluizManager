# PyLuiz Manager - Gerenciador de Instâncias Xephyr

Um gerenciador gráfico para criar, controlar e monitorar múltiplas instâncias do Xephyr em sistemas Linux.

## Características

- **Interface Gráfica Intuitiva**: Interface desenvolvida com tkinter
- **Múltiplas Instâncias**: Crie quantas instâncias do Xephyr precisar
- **Numeração Automática**: Sistema automático de numeração de displays
- **Controle Completo**: Iniciar, parar e remover instâncias individualmente
- **Monitoramento em Tempo Real**: Status atualizado automaticamente
- **Dimensões Personalizáveis**: Configure largura e altura de cada instância

## Pré-requisitos

- Python 3.6 ou superior
- Xephyr (parte do pacote xserver-xephyr)
- tkinter (geralmente incluído com Python)

### Instalação do Xephyr no Ubuntu/Debian:
```bash
sudo apt update
sudo apt install xserver-xephyr
```

### Instalação do Xephyr no Fedora/RHEL:
```bash
sudo dnf install xorg-x11-server-Xephyr
```

### Instalação do Xephyr no Arch Linux:
```bash
sudo pacman -S xorg-server-xephyr
```

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Executar a aplicação:
```bash
python main.py
```

ou

```bash
python gui.py
```

### Funcionalidades da Interface:

1. **Nova Instância**: 
   - Configure largura e altura desejadas
   - Clique em "Nova Instância" para criar
   - A aplicação automaticamente encontra o próximo display disponível

2. **Controle Individual**:
   - Selecione uma instância na lista
   - Use os botões "Iniciar", "Parar" ou "Remover"

3. **Controles Globais**:
   - "Parar Todas": Para todas as instâncias ativas
   - "Limpar Mortas": Remove instâncias que não estão mais rodando

### Teste via linha de comando:
```bash
python xephyr_manager.py
```

## Estrutura do Projeto

```
pyluizManager/
├── main.py              # Ponto de entrada da aplicação
├── gui.py               # Interface gráfica com tkinter
├── xephyr_manager.py    # Lógica de gerenciamento do Xephyr
├── requirements.txt     # Dependências Python
└── README.md           # Este arquivo
```

## Como Funciona

### XephyrManager
- Gerencia múltiplas instâncias do Xephyr
- Encontra automaticamente displays disponíveis
- Controla processos e monitora status

### XephyrInstance
- Representa uma instância individual do Xephyr
- Controla início, parada e monitoramento
- Gerencia parâmetros como dimensões da tela

### Interface Gráfica
- Lista todas as instâncias em tempo real
- Permite controle individual e em massa
- Interface responsiva e intuitiva

## Exemplos de Uso

### Desenvolvimento com Múltiplos Ambientes
Ideal para testar aplicações em múltiplos ambientes X11 isolados:

```bash
# Primeira instância para desenvolvimento
DISPLAY=:1 your-app

# Segunda instância para testes
DISPLAY=:2 your-test-suite
```

### Demonstrações e Apresentações
Isole aplicações para demonstrações:

```bash
# Instância dedicada para demonstração
DISPLAY=:3 presentation-app
```

## Solução de Problemas

### Xephyr não encontrado
Certifique-se de que o Xephyr está instalado:
```bash
which Xephyr
```

### Permissões de Display
Se houver problemas de permissão:
```bash
xauth list
```

### Instâncias "fantasma"
Use "Limpar Mortas" para remover instâncias que não respondem.

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

## Licença

Este projeto é open source. Use conforme necessário.

## Autor

Desenvolvido para facilitar o gerenciamento de instâncias Xephyr em ambientes de desenvolvimento Linux.
