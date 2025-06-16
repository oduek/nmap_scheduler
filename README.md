## Nmap_scheduler un script diseñado para ejecutar escaneos con Nmap de manera **agendada** y **programada**. Su propósito es permitir la ejecución de análisis fuera del horario laboral, evitando la necesidad de supervisión directa. 

## Requisitos
El único requisito en caso de linux (kali linux) para su funcionamiento es tener **Nmap** instalado en el sistema operativo. No requiere dependencias adicionales.

## Beneficios: 
  A diferencia de alternativas como el comando `at`, este script funciona de manera **independiente**, lo que lo hace ideal para entornos restringidos sin acceso a internet.

- **Salida de resultados en formatos estándar**  
  Los resultados del escaneo se guardan en **TXT** o **XML**, permitiendo su importación en herramientas como **Metasploit**.

- **Ejecución automática y validación horaria**  
  El script verifica constantemente la hora para asegurarse de ejecutarse en el momento programado.

## Nota importante
Si bien **Nmap Scheduler** es intuitivo de usar, algunas funciones avanzadas requieren conocimientos técnicos sobre escaneo de redes y programación de tareas.  

### Disclaimer de seguridad
El uso indebido de este script para actividades no autorizadas podría infringir regulaciones o políticas de seguridad. **El autor no se hace responsable del uso inapropiado de esta herramienta**. Úsalo con responsabilidad y dentro del marco legal.  

## USO
Se utiliza con la sentencia python nmap_scheduler.py



