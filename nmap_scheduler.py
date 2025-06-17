import subprocess
import time
import argparse
import datetime
import os
import sys # Importar sys para stdout.flush()

# Variable global para almacenar el estado de ejecución del script y los errores
script_status = {
    "last_scan_error_occurred": False,
    "last_scan_error_message": "",
    "predicted_error_message": ""
}

def ejecutar_nmap(nmap_command_list, output_dir, output_base_filename, output_formats):
    """
    Ejecuta un escaneo Nmap con el comando especificado y guarda los resultados.
    Muestra el progreso en vivo de Nmap.
    Actualiza el estado global de errores del script.

    Args:
        nmap_command_list (list): La lista de argumentos para el comando Nmap.
        output_dir (str): El directorio donde se guardarán los resultados.
        output_base_filename (str): El nombre base del archivo de salida proporcionado por el usuario.
        output_formats (list): Lista de formatos de salida deseados ('txt', 'xml').
    """
    global script_status # Declarar la intención de modificar la variable global

    script_status["last_scan_error_occurred"] = False
    script_status["last_scan_error_message"] = ""

    # Para genera un nombre de archivo único con marca de tiempo
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Limpia el nombre base para que sea seguro en el nombre de archivo
    safe_output_base_filename = "".join(c for c in output_base_filename if c.isalnum() or c in (' ', '.', '_')).strip()
    if not safe_output_base_filename:
        safe_output_base_filename = "nmap_scan" # Nombre por defecto si el usuario no introduce nada válido

    output_filepath_txt = os.path.join(output_dir, f"{safe_output_base_filename}_{timestamp}.txt")
    output_filepath_xml = os.path.join(output_dir, f"{safe_output_base_filename}_{timestamp}.xml")

    # Asegurarse de que -v (verbose) esté en el comando para obtener salida de progreso
    if "-v" not in nmap_command_list and "--verbose" not in nmap_command_list:
        nmap_command_list.append("-v")

    # Añadir opciones de formato de salida a la lista de comandos de Nmap
    if 'txt' in output_formats:
        nmap_command_list.extend(["-oN", output_filepath_txt])
        print(f"Los resultados en formato de texto se guardarán aquí: {output_filepath_txt}")
    if 'xml' in output_formats:
        nmap_command_list.extend(["-oX", output_filepath_xml])
        print(f"Los resultados en formato XML se guardarán aquí: {output_filepath_xml}")

    print(f"\n¡Todo listo! Voy a ejecutar Nmap con este comando: {' '.join(nmap_command_list)}")
    print("\n--- ¡Mira la magia de Nmap en acción! ---")

    full_nmap_stdout_output = []
    try:
        # Usar Popen para obtener la salida en tiempo real
        process = subprocess.Popen(nmap_command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        
        # Leer y mostrar la salida estándar de Nmap en tiempo real
        while True:
            output_line = process.stdout.readline()
            if output_line == '' and process.poll() is not None:
                break
            if output_line:
                print(output_line.strip())
                full_nmap_stdout_output.append(output_line)
            sys.stdout.flush()

        # Capturar el stderr despues de que el proceso termine
        stderr_output = process.stderr.read()

        # Esperar a que el proceso termine y obtener el código de retorno
        return_code = process.wait()

        print("--- Fin de la salida en vivo de Nmap ---\n")

        # Si se eligió la salida de texto, guardar la salida capturada
        if 'txt' in output_formats:
            with open(output_filepath_txt, "w") as archivo:
                archivo.write("".join(full_nmap_stdout_output))
                if stderr_output:
                    archivo.write("\n--- Errores/Advertencias de Nmap (stderr) ---\n")
                    archivo.write(stderr_output)
            print(f"Resultados de texto guardados en {output_filepath_txt}")
        
        # Si se eligió la salida XML, Nmap ya la guardó directamente
        if 'xml' in output_formats:
            print(f"Resultados XML guardados en {output_filepath_xml}")

        # Comprobar si Nmap finalizó con un código de error (distinto de 0)
        if return_code != 0:
            script_status["last_scan_error_occurred"] = True
            script_status["last_scan_error_message"] = (
                f"Nmap finalizó con código de salida {return_code}. "
                f"Esto indica un error en la ejecución de Nmap. ¡Ups! Algo no salió como esperabas. Stderr: \n{stderr_output}"
            )
            print(f"¡ALERTA DE ERROR!: {script_status['last_scan_error_message']}")
        elif stderr_output:
            # Nmap finalizó con código 0 (éxito), pero imprimió algo en stderr.
            # Esto suele ser una advertencia o mensaje informativo, no un error fatal.
            # No se marca 'last_scan_error_occurred' como True en este caso.
            print(f"Nmap completó, pero con algunas advertencias o mensajes en stderr:\n{stderr_output}")
            script_status["last_scan_error_message"] = ( # Se almacena el mensaje por si se necesita para un log más detallado
                f"Nmap completó con advertencias/mensajes en stderr: \n{stderr_output}"
            )

    except FileNotFoundError:
        script_status["last_scan_error_occurred"] = True
        script_status["last_scan_error_message"] = (
            "Error: Nmap no se encontró. Asegúrate de que Nmap esté instalado y en tu PATH. ¡Parece que Nmap no está disponible!"
        )
        print(script_status["last_scan_error_message"])
    except Exception as e:
        script_status["last_scan_error_occurred"] = True
        script_status["last_scan_error_message"] = (
            f"Ocurrió un error inesperado durante el escaneo o al guardar los resultados: {e}. ¡Esto es inesperado!"
        )
        print(script_status["last_scan_error_message"])

def main():
    """
    Función principal para configurar el programador de Nmap de forma interactiva.
    """
    global script_status # Declarar la intención de modificar la variable global

    # Obtener la hora actual del sistema en formato HH:MM
    current_time_str = datetime.datetime.now().strftime("%H:%M")

    parser = argparse.ArgumentParser(description="Programa un escaneo Nmap para ejecutarse a una hora específica.")
    # Removido el valor por defecto aquí para que el input() se pregunte siempre si no se especifica por línea de comandos
    parser.add_argument("--hora", type=str,
                        help=f"La hora programada para el escaneo (formato HH:MM). Por defecto: la hora actual del sistema ({current_time_str})")
    parser.add_argument("--fecha", type=str, default=None,
                        help="La fecha programada para el escaneo (formato YYYY-MM-DD).")
    parser.add_argument("--salida", type=str, default=None,
                        help="El directorio donde se guardarán los resultados.")
    parser.add_argument("--nombre_archivo", type=str, default=None,
                        help="El nombre base del archivo de salida para los resultados.")

    args = parser.parse_args()

    print("¡Hola! Aqui podemos programar escaneos con Nmap. ¡Vamos a configurarlo!")

    # --- Obtener información de programación y salida ---
    # Si el usuario no proporcionó --hora en la línea de comandos, se le pregunta, ofreciendo la hora actual como ejemplo.
    if args.hora:
        hora_programada_str = args.hora
    else:
        hora_input = input(f"¿A qué hora quieres que iniciemos el escaneo? (HH:MM, por ejemplo, {current_time_str}. Presiona Enter para usar la hora actual): ")
        # Si el usuario presiona Enter sin introducir nada, usa la hora actual del sistema en horario militar (24 horas)
        hora_programada_str = hora_input if hora_input else current_time_str 

    fecha_programada_str = args.fecha if args.fecha else input("¿Para qué fecha quieres programarlo? (YYYY-MM-DD, por ejemplo, 2026-12-24): ")
    output_dir = args.salida if args.salida else input("¿Dónde quieres que guardemos los resultados? (Ruta del directorio, ej. /home/kali/Desktop): ")
    output_base_filename = args.nombre_archivo if args.nombre_archivo else input("¡Por favor dame un nombre para guardar tu archivo de resultados! (ej. mi_escaneo_web): ")
        
    # Pre-check for output directory existence
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"¡Perfecto! El directorio '{output_dir}' ha sido creado.")
        except OSError as e:
            script_status["predicted_error_message"] = (
                f"¡Ups! No pude crear el directorio de salida '{output_dir}': {e}. "
                "Esto podría causar problemas al guardar los resultados. ¡Revisa los permisos!"
            )
            print(script_status["predicted_error_message"])
    elif not os.path.isdir(output_dir):
        script_status["predicted_error_message"] = (
            f"¡ALERTA! La ruta '{output_dir}' ya existe, pero no es un directorio. "
            "Esto podría causar problemas al guardar los resultados. ¡Asegúrate de que sea una carpeta!"
        )
        print(script_status["predicted_error_message"])


    target_info = "" # Para el banner
    nmap_command_base = ["nmap", "-sV"] # Opciones base, detección de versión

    # --- Opciones de objetivos (-iL o IP/rango) ---
    use_il = input("¿Prefieres usar un archivo con una lista de objetivos (-iL)? (s/n): ").lower()
    if use_il == 's':
        file_path = input("¡Entendido! Dame la ruta completa de tu archivo de objetivos (ej. /ruta/a/objetivos.txt): ")
        if not os.path.exists(file_path):
            script_status["predicted_error_message"] += (
                f"\n¡Cuidado! El archivo de objetivos '{file_path}' no existe. "
                "Nmap podría quedarse sin objetivos o fallar. ¡Verifica la ruta!"
            )
            print(script_status["predicted_error_message"])
        nmap_command_base.extend(["-iL", file_path])
        target_info = f"Archivo de objetivos: {file_path}"
    else:
        target_ip = input("Ok, entonces, ¿cuál es la dirección IP o el rango de IPs que quieres escanear? (ej. 127.0.0.1 o 192.168.1.0/24): ")
        nmap_command_base.append(target_ip)
        target_info = f"IP/Rango objetivo: {target_ip}"

    # --- Opciones de puertos ---
    port_selection_text = "Sin especificar"
    port_option = input("¿Cómo quieres que Nmap especifique los puertos? (1: --top-ports, 2: -p- (todos los puertos), 3: Lista específica, 4: Dejar que Nmap decida): ")

    if port_option == '1':
        try:
            top_ports_count = int(input("¿Cuántos de los puertos más comunes quieres escanear? (ej. 2500): "))
            nmap_command_base.extend(["--top-ports", str(top_ports_count)])
            port_selection_text = f"--top-ports {top_ports_count}"
        except ValueError:
            script_status["predicted_error_message"] += (
                "\n¡Uy! La cantidad de top-ports no es un número válido. Se omitirá esta opción."
            )
            print(script_status["predicted_error_message"])
    elif port_option == '2':
        nmap_command_base.append("-p-") # Escanear todos los puertos
        port_selection_text = "-p- (todos los puertos)"
    elif port_option == '3':
        ports_list = input("¡Claro! Escribe los puertos específicos que quieres escanear (separados por comas, ej. 22,80,443,3389): ")
        nmap_command_base.extend(["-p", ports_list])
        port_selection_text = f"Puertos específicos: {ports_list}"
    # Si la opcion es '4' o cualquier otra cosa, no se añade opción de puertos, Nmap usará sus puertos por defecto

    # --- Opciones extras de Nmap ---
    extra_options_str = input("¿Hay alguna otra opción avanzada de Nmap que quieras añadir? (ej. -O -A --script vuln --open -v4. Deja en blanco si no hay más): ")
    if extra_options_str:
        # Divide el string con opciones extras y añáde a la lista de comandos
        nmap_command_base.extend(extra_options_str.split())
    
    extra_options_display = extra_options_str if extra_options_str else "Ninguna"

    # --- Para el formato de salida ---
    output_formats_chosen = []
    output_format_choice = input("¿En qué formato quieres los resultados? (1: Solo en texto -oN, 2: Solo en XML -oX, 3: Ambos formatos): ")
    if output_format_choice == '1':
        output_formats_chosen.append('txt')
        output_formats_display = "Texto (-oN)"
    elif output_format_choice == '2':
        output_formats_chosen.append('xml')
        output_formats_display = "XML (-oX)"
    elif output_format_choice == '3':
        output_formats_chosen.extend(['txt', 'xml'])
        output_formats_display = "Texto (-oN) y XML (-oX)"
    else:
        print("Opción de formato de salida inválida. Solo mostraré la salida en la consola.")
        output_formats_display = "Solo consola (Sin archivo -oN/-oX)"


    try:
        programada_dt = datetime.datetime.strptime(f"{fecha_programada_str} {hora_programada_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        script_status["predicted_error_message"] += (
            "\n¡Error en la fecha u hora que me diste! Asegúrate de usar YYYY-MM-DD y HH:MM. ¡No te preocupes, puedes intentarlo de nuevo!"
        )
        print(script_status["predicted_error_message"])
        return # Salir del script si el formato es incorrecto

    # --- Banner de Opciones de Escaneo ---
    print("\n" + "="*50)
    print("           RESUMEN DEL ESCANEO NMAP PROGRAMADO")
    print("")
    print(" Desarrollado por Oduek ")
    print("")
    print(" https://github.com/oduek ")
    print("")
    print("="*50)
    print(f"Programado para: {fecha_programada_str} a las {hora_programada_str}")
    print(f"Objetivo(s):     {target_info}")
    print(f"Puertos a escanear: {port_selection_text}")
    print(f"Opciones Nmap extra: {extra_options_display}")
    print(f"Resultados guardados en: {output_dir}")
    print(f"Nombre de archivo base: {output_base_filename}_<marca_de_tiempo>.txt/xml")
    print(f"Formato(s) de salida: {output_formats_display}")
    print(f"El comando Nmap será: {' '.join(nmap_command_base)}")
    
    # Muestra el estado de errores 
    if script_status["predicted_error_message"]:
        print("\n" + "-"*50)
        print("!!! ¡ALERTA! HAY ALGUNAS ADVERTENCIAS O ERRORES !!!")
        print(script_status["predicted_error_message"])
        print("-"*50)
    
    print("="*50 + "\n")
    print("¡Listo! El escaneo está programado. Estare valindando la hora hasta que se cumpla la hora indicada.")

    while True:
        hora_actual_dt = datetime.datetime.now()
        
        if hora_actual_dt >= programada_dt:
            print(f"\n¡Llegó la hora! Son las {hora_actual_dt.strftime('%Y-%m-%d %H:%M')}. ¡Comenzando el escaneo Nmap ahora mismo!...")
            ejecutar_nmap(nmap_command_base, output_dir, output_base_filename, output_formats_chosen)
            
            # Aqui muestra el estado del último escaneo
            if script_status["last_scan_error_occurred"]:
                print("\n" + "!"*50)
                print("!!! ¡TERMINÓ CON ERRORES! REVISA EL MENSAJE ANTERIOR PARA MÁS DETALLES !!!")
                print(script_status["last_scan_error_message"])
                print("!"*50 + "\n")
            else:
                print("\n" + "*"*50)
                print("¡Escaneo Nmap completado exitosamente! Todo salió bien.")
                print("*"*50 + "\n")

            break # Salir del bucle después de ejecutar el escaneo
        else:
            # Calcular el tiempo restante para una visualización más amigable
            tiempo_restante = programada_dt - hora_actual_dt
            dias = tiempo_restante.days
            horas, rem = divmod(tiempo_restante.seconds, 3600)
            minutos, segundos = divmod(rem, 60)
            
            mensaje_espera = f"Aún esperando la hora programada ({programada_dt.strftime('%Y-%m-%d %H:%M')}). "
            if dias > 0:
                mensaje_espera += f"Faltan {dias} días, {horas} horas, {minutos} minutos y {segundos} segundos."
            else:
                mensaje_espera += f"Faltan {horas} horas, {minutos} minutos y {segundos} segundos."
            
            print(mensaje_espera, end='\r')
        
        time.sleep(20) # Sirve para revisar la hora cada 20 segundos, aqui se puede modificar el tiempo para que sea mas rapido o mas lento la validación.

if __name__ == "__main__":
    main()
