import os
import sys
import re
import signal
import datetime
from colorama import Fore, Style, init
from contextlib import redirect_stdout
from scripts import (
    check_user_enumeration,
    check_xmlrpc,
    scan_sensitive_files,
    detect_wp_version,
    check_rest_api
)

# Configuración inicial
init(autoreset=True)
audit_interrupted = False  # Nueva variable global

# Manejo mejorado de Ctrl+C
def signal_handler(sig, frame):
    global audit_interrupted
    audit_interrupted = True
    print(f"\n{Style.BRIGHT}{Fore.RED}❌ AUDITORÍA CANCELADA! {Fore.WHITE}Deteniendo procesos...{Style.RESET_ALL}")
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

# Configuración de herramientas (Versión de WP primero)
TOOLS = {
    "1": {"name": "Detectar Versión de WordPress", "func": detect_wp_version},
    "2": {"name": "Detectar Enumeración de Usuarios", "func": check_user_enumeration},
    "3": {"name": "Analizar XML-RPC", "func": check_xmlrpc},
    "4": {"name": "Escáner de Archivos Sensibles", "func": scan_sensitive_files},
    "5": {"name": "Auditar REST API", "func": check_rest_api},
    "6": {"name": "Ejecutar Auditoría Completa", "func": None},
    "7": {"name": "Salir del Programa", "func": None}
}

class DualOutput:
    """Clase para manejar salida dual (consola + archivo)"""
    def __init__(self, console, log_file):
        self.console = console
        self.log_file = log_file
        self.ansi_escape = re.compile(r'\x1b\[[0-9;]*m')

    def write(self, text):
        self.console.write(text)
        cleaned_text = self.ansi_escape.sub('', text)
        self.log_file.write(cleaned_text)

    def flush(self):
        self.console.flush()
        self.log_file.flush()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = f"""
{Style.BRIGHT}{Fore.CYAN}
██╗    ██╗██████╗  █████╗ ████████╗
██║    ██║██╔══██╗██╔══██╗╚══██╔══╝
██║ █╗ ██║██████╔╝███████║   ██║   
██║███╗██║██╔═══╝ ██╔══██║   ██║   
╚███╔███╔╝██║     ██║  ██║   ██║   
 ╚══╝╚══╝ ╚═╝     ╚═╝  ╚═╝   ╚═╝   
{Fore.MAGENTA}─────────────────────────────────────────────
{Fore.WHITE}       WordPress Professional Audit Tool
{Fore.CYAN}          Versión 1.0 · Ethical Hacking
{Fore.YELLOW}         Creado por Santitub | {Fore.BLUE}https://github.com/Santitub
{Fore.MAGENTA}─────────────────────────────────────────────
{Style.RESET_ALL}
"""
    print(banner)

def get_target_url():
    print(f"{Style.BRIGHT}{Fore.MAGENTA}►► {Fore.CYAN}PASO 1/3: {Fore.WHITE}CONFIGURACIÓN INICIAL")
    return input(f"\n{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}URL objetivo {Fore.YELLOW}(ej: https://ejemplo.com){Fore.WHITE}: ").strip().rstrip('/')

def print_menu(url):
    clear_console()
    print(f"""
{Style.BRIGHT}{Fore.MAGENTA}►► {Fore.CYAN}PASO 2/3: {Fore.WHITE}MENÚ PRINCIPAL
{Fore.MAGENTA}─────────────────────────────────────────────
{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Objetivo: {Fore.YELLOW}{url}
""")
    for key in TOOLS:
        print(f"{Style.BRIGHT}{Fore.CYAN} [{Fore.MAGENTA}{key}{Fore.CYAN}] {Fore.WHITE}{TOOLS[key]['name']}")
    print(f"{Fore.MAGENTA}─────────────────────────────────────────────")

def run_tool(url, choice):
    global audit_interrupted
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
    log_file = os.path.join(log_dir, f"auditoria_{timestamp}.txt")

    with open(log_file, 'w') as f:
        dual = DualOutput(sys.stdout, f)
        with redirect_stdout(dual):
            if choice == '6':
                print(f"{Style.BRIGHT}{Fore.CYAN}► {Fore.WHITE}Ejecutando auditoría completa... {Fore.YELLOW}🛡️\n")
                for key in [k for k in TOOLS if k not in ("6", "7")]:
                    if audit_interrupted:
                        break
                    print(f"{Fore.MAGENTA}────── {TOOLS[key]['name'].upper()} {Fore.MAGENTA}──────")
                    TOOLS[key]['func'](url)
                    print()
            else:
                print(f"{Style.BRIGHT}{Fore.CYAN}► {Fore.WHITE}Ejecutando: {Fore.YELLOW}{TOOLS[choice]['name']}...\n")
                TOOLS[choice]['func'](url)
    
    print(f"\n{Style.BRIGHT}{Fore.GREEN}[✓]{Fore.WHITE} Log guardado en: {log_file}")

def main():
    print_banner()
    url = get_target_url()
    
    while True:
        print_menu(url)
        choice = input(f"{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Selección {Fore.YELLOW}(1-7){Fore.WHITE}: ").strip()

        if choice == '7':
            print(f"\n{Style.BRIGHT}{Fore.CYAN}► {Fore.MAGENTA}¡Auditoría finalizada! {Fore.YELLOW}🛡️\n")
            break
            
        if choice in ['1', '2', '3', '4', '5', '6']:
            clear_console()
            run_tool(url, choice)
            input(f"\n{Style.BRIGHT}{Fore.CYAN}↳ {Fore.WHITE}Presiona Enter para continuar...")
            
if __name__ == "__main__":
    main()