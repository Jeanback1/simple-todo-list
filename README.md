# Simple TO DO list

Aplicación de terminal (TUI) para gestionar listas de tareas con sub-secciones y sub-tareas anidadas. Permite crear, abrir y marcar listas en cualquier directorio del sistema, almacenadas como archivos Markdown estándar que cualquier modelo de IA puede leer directamente.

## Características

- Listas como archivos: cada lista es un archivo Markdown en la ruta que elijas. Puedes tener tantas listas como quieras, en cualquier directorio, y abrirlas a voluntad.
- Sub-secciones: agrupa tareas por categorías dentro de una misma lista.
- Sub-tareas anidadas: hasta 7 niveles de profundidad.
- Completado automático: un elemento con sub-tareas se marca como completado solo cuando todas sus sub-tareas lo están.
- Propagación de estado: al marcar o desmarcar un elemento padre, el estado se propaga a todos sus descendientes.
- Legible por IA: el formato es checklist Markdown estándar, consumible por cualquier modelo sin conversión previa.
- Acceso por línea de comandos: subcomandos para volcar el contenido de una lista en texto plano o resumir sus secciones.

## Requisitos

- Python 3.10 o superior.
- La librería [Textual](https://textual.textualize.io/) (se instala en un entorno virtual).

## Instalación

La aplicación se instala en un entorno virtual propio para no interferir con el Python del sistema.

```bash
# 1. Clona el repositorio
git clone https://github.com/Jeanback1/simple-todo-list.git
cd simple-todo-list

# 2. Crea el entorno virtual e instala Textual
python3 -m venv venv
./venv/bin/pip install textual

# 3. Opcional: crea un enlace para ejecutarla desde cualquier parte
ln -s "$(pwd)/lista.py" ~/.local/bin/lista
# Asegúrate de que ~/.local/bin esté en tu PATH
```

## Uso

### Abrir una lista en la interfaz

```bash
lista ~/documentos/tareas.md
```

Si el archivo no existe, se crea automáticamente. También puedes pasar un directorio:

```bash
lista ~/proyectos/website
```

En ese caso se abre (o se crea) el archivo `website.md` dentro de ese directorio.

### Leer una lista (legible por IA)

```bash
lista ver ~/documentos/tareas.md
```

Vuelca el contenido completo de la lista en texto plano, respetando las sub-secciones y la anidación.

### Resumen de secciones

```bash
lista secciones ~/documentos/tareas.md
```

Muestra las secciones de la lista con el número de tareas pendientes en cada una.

## Atajos de teclado

| Tecla | Acción |
|-------|--------|
| `j` / `k` o `↑` / `↓` | Navegar entre elementos |
| `espacio` / `Enter` | Marcar o desmarcar (propaga a sub-tareas) |
| `a` | Añadir sub-tarea al elemento seleccionado |
| `n` | Añadir un elemento raíz nuevo |
| `s` | Añadir una sección nueva |
| `r` | Renombrar la sección actual |
| `x` | Eliminar el elemento seleccionado |
| `q` | Guardar y salir |

## Formato del archivo

Las listas se guardan como checklist Markdown estándar. Un elemento con sub-tareas se considera completado cuando todas sus sub-tareas lo están.

```markdown
# Proyecto
## Fase 1
- [x] Planear
- [ ] Desarrollar
  - [ ] Backend
    - [ ] API
    - [ ] Base de datos
  - [ ] Frontend
## Fase 2
- [ ] Lanzar
```

## Uso con agentes de IA

Simple TO DO list está diseñada para que un modelo de IA (agente) pueda leer y mantener las listas directamente. Como cada lista es un archivo Markdown con formato estándar, un agente puede procesarlas sin conversión previa y sin abrir la interfaz gráfica.

### Lectura por un agente

El subcomando `ver` imprime la lista completa en texto plano, respetando sub-secciones y anidación:

```bash
lista ver ~/documentos/tareas.md
```

El agente lee la salida, identifica los pendientes y puede responder agrupando por sección (por ejemplo: "te falta Manzanas en Frutas y Leche en Lácteos").

### Edición por un agente

Como el formato es Markdown puro, el agente puede modificar el archivo directamente:

- Marcar un elemento: cambiar `- [ ] Texto` por `- [x] Texto`. Si el elemento tiene sub-tareas, deben marcarse todas para que el padre se considere completado (el estado del padre es derivado).
- Añadir un elemento raíz: insertar `- [ ] Texto` en la sección correspondiente.
- Añadir una sub-tarea: insertar `  - [ ] Texto` (dos espacios) bajo el elemento padre.
- Añadir una sección: insertar `## Nombre` al final.

Para ediciones programáticas es recomendable parsear el archivo en estructura de árbol, modificar los nodos y volver a serializar, respetando así el orden y la anidación.

### Configurar un agente de IA para usarla

El agente debe tener acceso al comando `lista` y a los archivos de las listas. La configuración depende de cada plataforma, pero el patrón general es:

1. Instalar la aplicación (ver sección Instalación) en la misma máquina donde corre el agente, o en una máquina a la que el agente pueda acceder por SSH.
2. Darle al agente una instrucción permanente o un "skill" que indique cómo usar el comando. Ejemplo de instrucción para el agente:

```
Para gestionar listas de tareas, usa el comando `lista`:
- lista ver <ruta>       para leer una lista (responde agrupando por secciones)
- lista secciones <ruta> para ver el resumen por secciones
- Edita el archivo .md directamente para marcar o añadir elementos,
  respetando la indentación (2 espacios por nivel) y la regla de que
  un elemento con sub-tareas se completa solo cuando todas lo están.
```

3. Si el agente corre en una máquina distinta a la de las listas, asegurarse de que pueda ejecutar el comando por SSH sobre el usuario dueño de los archivos (usando rutas absolutas).

Algunas plataformas (como Hermes Agent) permiten crear una skill persistente con estas instrucciones, de modo que el agente las cargue automáticamente cuando el usuario le pida interactuar con sus listas.

## Documentación

- [Guía de uso](docs/uso.md): operaciones detalladas, buenas prácticas y resolución de problemas.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE).
