# Pulse SMS

Dashboard para consolidar y monitorear automáticamente los archivos CSV de mensajería ubicados en esta carpeta.

## Ejecución

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La aplicación descubre todos los archivos `*.csv` al iniciar. Para incorporar un nuevo corte, déjalo en esta misma carpeta y recarga el navegador. Si el archivo más reciente contiene la misma combinación de agente, tipo MIME, fecha y hora que un corte anterior, reemplaza ese registro para evitar doble conteo.

## Estructura de los CSV

Cada archivo debe incluir estas columnas:

```text
agent,mime_type,fecha_sent,hora_sent,mensajes_enviados,mensajes_leidos,mensajes_fallidos,mensajes_facturables
```

Las fechas deben ser interpretables por pandas y las horas deben estar entre 0 y 23. Los conteos vacíos se consideran cero y los registros sin fecha u hora válida se descartan.

## Métricas

- Mensajes enviados, leídos, fallidos y facturables.
- Porcentajes de leídos, fallidos y facturables sobre mensajes enviados.
- Comparación del mes más reciente contra el mismo día de corte del mes anterior.
- Variaciones seleccionables por métrica, mes, día y hora.
- Mapas de calor por día de la semana y hora para volumen y calidad.
- Matriz temporal e insights operativos dinámicos.