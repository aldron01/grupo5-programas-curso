# Flujo del sistema

## Inicio

Al abrir `frontend/Demo.html`, el sistema inicia con:

- Estado `BORRADOR`.
- Versión `1`.
- Rol seleccionado: `Docente`.

El selector de rol permite simular las acciones de Docente, Coordinador
académico y Decanatura. No es un mecanismo de autenticación: los permisos se
controlan en el navegador.

## Flujo del programa

```text
BORRADOR
  |
  | Docente completa su nombre y selecciona "Enviar a revisión"
  v
EN REVISIÓN
  |
  | Coordinación académica registra su nombre
  |
  +-- Devolver al docente --> DEVUELTO
  |                              |
  |                              | Docente edita, guarda y vuelve a enviar
  |                              +--------------------------> EN REVISIÓN
  |
  +-- Aprobar ----------------> APROBADO
                                  |
                                  | Decanatura registra su nombre
                                  |
                                  +-- Autorizar -----------> AUTORIZADO
                                  |                           |
                                  |                           | Coordinación académica
                                  |                           | registra su nombre
                                  |                           | y crea una versión
                                  |                           v
                                  |                        BORRADOR
                                  |                        (versión siguiente)
                                  |
                                  +-- Enviar nuevamente ---> EN REVISIÓN
                                      a revisión               |
                                                                | Coordinación académica
                                                                | vuelve a revisar
                                                                +--> DEVUELTO o APROBADO
```

## Acciones y permisos

| Rol | Estado | Acciones disponibles |
| --- | --- | --- |
| Docente | `BORRADOR` o `DEVUELTO` | Editar el programa, guardar borrador y enviarlo a revisión. |
| Coordinador académico | `EN REVISIÓN` | Registrar su nombre, devolver el programa o aprobarlo. |
| Decanatura | `APROBADO` | Registrar su nombre, autorizar la versión o enviarla nuevamente a revisión académica. |
| Coordinador académico | `AUTORIZADO` | Registrar su nombre y crear la siguiente versión en estado `BORRADOR`. |

Los campos de las secciones del programa solo se pueden editar como Docente
cuando el estado es `BORRADOR` o `DEVUELTO`.

El nombre de Docencia se puede editar en esos mismos casos. El nombre de
Coordinación académica se puede editar cuando ese rol está seleccionado y el
estado es `EN REVISIÓN` o `AUTORIZADO`. El nombre de Decanatura se puede editar
cuando Decanatura está seleccionada y el estado es `APROBADO`.

Para aprobar o devolver el programa, Coordinación académica debe haber
completado su nombre. Para autorizar, Decanatura debe haber completado su
nombre. La acción de Decanatura para enviar nuevamente a revisión solo requiere
que el estado sea `APROBADO`.

## Guardado y versiones

- «Guardar borrador» muestra una confirmación y deja el estado en `BORRADOR`.
  No guarda los datos en un archivo ni en la API.
- «Cancelar cambios» solicita confirmación, pero no revierte ni restaura los
  valores anteriores.
- Crear una nueva versión incrementa el número y la inicia en `BORRADOR`.
- El estado y el número de versión solo viven en la página; al recargar se
  reinician a `BORRADOR` y versión `1`.
- La interfaz no está conectada a la API ni a `programas.json`; por eso, los
  cambios del formulario no persisten al recargar.

## Vista previa e impresión

- «Vista previa PDF» genera una vista institucional con el contenido actual de
  todas las secciones del programa, mostrando sus campos como texto.
- La vista incluye asignatura, facultad, versión, fecha, estado, los nombres de
  Docencia, Decanatura y Coordinación académica, además de espacios de firma.
- La leyenda indica «Documento autorizado» solo cuando el estado es
  `AUTORIZADO`; en los demás estados indica que no tiene autorización vigente.
- «Imprimir / Guardar PDF» abre el diálogo de impresión del navegador.
- «Volver al editor» cierra la vista previa y vuelve a mostrar el formulario.
