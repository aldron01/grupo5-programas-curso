# Flujo del sistema

```text
INICIO
  |
  v
Iniciar el servidor y abrir la aplicación
  |
  v
Estado: BORRADOR | Versión: 1 | Rol inicial: DOCENTE
  |
  v
DOCENTE escribe su nombre y edita el programa
  (el nombre queda bloqueado al enviar a revisión)
  |
  +-- Guardar borrador
  |     +--> Muestra confirmación en pantalla
  |     +--> No guarda los datos en un archivo
  |
  +-- Cancelar cambios
  |     +--> Pide confirmación
  |     +--> No restaura los valores anteriores
  |
  +-- Enviar a revisión
        |
        +--> ¿Rol Docente y nombre del docente escrito?
              |
              +-- No --> Muestra aviso y sigue en borrador
              |
              +-- Sí --> Estado: EN REVISIÓN
                           |
                           v
                    COORDINADOR escribe su nombre y revisa
                    (el nombre queda bloqueado al devolver o aprobar)
                           |
                    +------+------+
                    |             |
                 Devolver       Aprobar
                    |             |
                    v             v
              Estado: DEVUELTO  Estado: APROBADO
                    |                  |
                    |                  v
                    |          DECANO escribe su nombre
                    |          y autoriza la versión
                    |          (el nombre queda bloqueado al autorizar)
                    |                  |
                    |                  v
                    |          Estado: AUTORIZADO
                    |                  |
                    |                  v
                    |          DECANO crea versión
                    |                  |
                    +<-----------------+
                         Nueva versión:
                         BORRADOR

VISTA PREVIA / PDF
  Vista previa PDF
       +--> Genera una hoja institucional con el contenido del formulario
       +--> Muestra todas las secciones como texto y tablas de solo lectura
       +--> Incluye Autorización: elaborado por, revisor, autoridad, fecha y observaciones
       +--> Deja las líneas de firma sin nombres para firmar manualmente al imprimir
       |
       +--> Imprimir / Guardar PDF
       |       +--> Abre el diálogo de impresión del navegador
       |
       +--> Volver al editor
               +--> Reactiva los campos y botones

FIN
```

## Notas

- Los roles disponibles son Docente, Coordinador y Decano. No hay rol
  Administrador.
- El Decano puede crear una nueva versión solamente cuando el estado es
  `AUTORIZADO`.
- Cada nombre de responsable solo se puede editar con el rol y en la etapa
  correspondiente. Si el flujo vuelve al borrador para una nueva revisión o
  una nueva versión, los nombres pueden editarse de nuevo cuando llegue su
  etapa.
- Los estados y el número de versión se manejan en la página. Al recargar, se
  reinician a `BORRADOR` y versión `1`.
- La API y `programas.json` existen, pero la interfaz actual no está conectada
  a ellos; por eso, el formulario y el flujo no persisten sus cambios.
