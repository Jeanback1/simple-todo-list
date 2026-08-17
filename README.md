# lista

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
git clone https://github.com/Jeanback1/lista.git
cd lista

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

## Documentación

- [Guía de uso](docs/uso.md): operaciones detalladas, buenas prácticas y resolución de problemas.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE).
