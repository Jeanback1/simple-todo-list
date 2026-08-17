# Guía de uso

Esta guía detalla las operaciones de `lista`, sus convenciones de formato y los casos de uso más frecuentes.

## Índice

1. [Conceptos](#conceptos)
2. [Apertura de listas](#apertura-de-listas)
3. [Operaciones en la interfaz](#operaciones-en-la-interfaz)
4. [Anidación de sub-tareas](#anidación-de-sub-tareas)
5. [Completado automático](#completado-automático)
6. [Lectura por línea de comandos](#lectura-por-línea-de-comandos)
7. [Formato de archivo](#formato-de-archivo)
8. [Resolución de problemas](#resolución-de-problemas)

## Conceptos

Una lista consta de tres niveles de organización:

- **Título**: el encabezado principal de la lista (`# Título`). Se deriva del nombre del archivo si no se especifica uno.
- **Sección**: agrupa tareas relacionadas dentro de la lista (`## Sección`).
- **Elemento**: una tarea individual, representada por un checkbox (`- [ ]` o `- [x]`).

Los elementos pueden contener sub-tareas, formando un árbol de hasta 7 niveles de profundidad.

## Apertura de listas

Cada lista es un archivo Markdown independiente. Puedes colocarlos en cualquier directorio.

```bash
# Abrir (o crear) una lista específica
lista /ruta/a/mi-lista.md

# Abrir la lista del directorio actual
lista .

# Abrir la lista de un directorio concreto (crea <nombre>.md dentro)
lista /ruta/proyecto
```

Al salir de la interfaz con `q`, los cambios se guardan automáticamente en el archivo.

## Operaciones en la interfaz

La navegación se realiza con `j`/`k` o las flechas. El elemento seleccionado se resalta con un fondo azul y un puntero.

- `a` añade una sub-tarea al elemento seleccionado. Si el elemento ya está en el nivel máximo de profundidad (7), se muestra un aviso y no se añade nada.
- `n` añade un elemento raíz (nivel 1) a la sección actual.
- `espacio` o `Enter` alterna el estado de marcado.
- `s` crea una sección nueva al final de la lista.
- `r` renombra la sección actual.
- `x` elimina el elemento seleccionado junto con todas sus sub-tareas.
- `q` guarda y cierra.

## Anidación de sub-tareas

Para crear un árbol de tareas:

1. Pulsa `n` para crear el elemento raíz.
2. Con el cursor sobre ese elemento, pulsa `a` para añadir una sub-tarea.
3. Repite `a` para bajar un nivel más (hasta 7 niveles).

El cursor se coloca automáticamente sobre la sub-tarea recién creada, lo que facilita encadenar niveles.

## Completado automático

La regla de completado es la siguiente:

- Un elemento **sin** sub-tareas se marca o desmarca manualmente.
- Un elemento **con** sub-tareas se considera completado solo cuando **todas** sus sub-tareas lo están. Este estado se calcula de forma derivada: si desmarcas una sub-tarea, el padre deja de estar completado.

Además, al marcar o desmarcar un elemento padre con `espacio`, el estado se propaga a todos sus descendientes. Esto es útil para completar o vaciar un subárbol entero de una sola vez.

## Lectura por línea de comandos

Los subcomandos permiten leer listas sin abrir la interfaz, lo que es útil para scripts o para que un modelo de IA procese el contenido.

```bash
# Ver el contenido completo
lista ver /ruta/a/mi-lista.md

# Ver un resumen por secciones
lista secciones /ruta/a/mi-lista.md
```

El subcomando `ver` imprime el checklist respetando la anidación y termina con el número total de pendientes.

## Formato de archivo

Las listas son archivos Markdown estándar. La indentación se hace con dos espacios por nivel. Los archivos creados por la aplicación siguen siempre esta estructura.

```markdown
# Título de la lista
## Sección 1
- [ ] Tarea pendiente
  - [ ] Sub-tarea A
  - [ ] Sub-tarea B
- [x] Tarea completada
## Sección 2
- [ ] Otra tarea
```

Notas sobre el formato:

- El archivo se puede editar a mano con cualquier editor de texto.
- El parser tolera la anidación con un número arbitrario de espacios; la profundidad se calcula dividiendo la indentación entre dos.
- Si una lista existente usa un nivel de anidación superior a 7, se recorta a 7 al guardarla.

## Resolución de problemas

**La interfaz no muestra las tareas añadidas.**
Verifica que el archivo de la lista se haya creado y tenga contenido con `lista ver /ruta/a/mi-lista.md`. Si el archivo es correcto y el problema persiste, actualiza Textual: `./venv/bin/pip install --upgrade textual`.

**No puedo ejecutar `lista` como comando.**
Asegúrate de que `~/.local/bin` esté en tu `PATH` y de que el enlace simbólico apunte al `lista.py` del repositorio.

**El límite de profundidad impide añadir más sub-tareas.**
Es un límite deliberado de 7 niveles para mantener la interfaz manejable. Si lo necesitas mayor, ajusta la constante `MAX_DEPTH` en `lista.py` y vuelve a instalar.
