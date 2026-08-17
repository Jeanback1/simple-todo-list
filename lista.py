#!/usr/bin/env python3
"""lista - checklist TUI por archivos Markdown con sub-secciones y sub-items.

Uso:
  lista <ruta> [--nuevo]     Abre la lista en TUI (crea el .md si no existe).
  lista ver <ruta>           Vuelca el checklist en texto plano (legible por IA).
  lista secciones <ruta>     Muestra solo las secciones y su conteo pendiente.

El archivo usa checklist estándar de Markdown con anidación:
  # Título
  ## Sección
  - [ ] Tarea
    - [ ] Subtarea A
      - [ ] Sub-sub
  - [x] Hecho

Un item con sub-items se considera completado cuando TODOS sus sub-items
están completados. Marcar/desmarcar un item padre propaga el estado a todos
sus descendientes.
"""

import os
import re
import sys
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, Input, Button, Label, Footer

MAX_DEPTH = 7  # niveles máximos de anidación (nivel 1 = item raíz, 7 = más profundo)

# ---------------------------------------------------------------- modelo ----

ITEM_RE = re.compile(r"^(\s*)- \[( |x|X)\] (.*)$")
SECTION_RE = re.compile(r"^##\s+(.*)$")
TITLE_RE = re.compile(r"^#\s+(.*)$")


def nodo(texto, checked=False):
    return {"text": texto, "checked": checked, "children": []}


def esta_completado(node):
    """Un item sin hijos es completado según su flag; con hijos, derivado:
    completado solo si TODOS sus sub-items lo están."""
    if not node["children"]:
        return node["checked"]
    return all(esta_completado(c) for c in node["children"])


def set_todos(node, valor):
    """Marca/desmarca recursivamente todos los descendientes (hojas) de un nodo."""
    if not node["children"]:
        node["checked"] = valor
    else:
        for c in node["children"]:
            set_todos(c, valor)


def leer_lista(path):
    """Parsea un .md a estructura de árbol. Devuelve (path, titulo, secciones).
    secciones: [{name, roots: [nodo]}]. Cada nodo: {text, checked, children}."""
    if not path.exists():
        return path, path.stem.replace("_", " ").replace("-", " ").title(), []
    secciones = []
    titulo = None
    cur = None
    levels = []  # levels[d] = último nodo en profundidad d (0 = raíz)
    texto = path.read_text(encoding="utf-8", errors="replace")
    for linea in texto.splitlines():
        m = TITLE_RE.match(linea)
        if m:
            titulo = m.group(1).strip()
            continue
        m = SECTION_RE.match(linea)
        if m:
            cur = {"name": m.group(1).strip(), "roots": []}
            secciones.append(cur)
            levels = []
            continue
        m = ITEM_RE.match(linea)
        if m:
            indent = len(m.group(1))
            depth = indent // 2
            checked = m.group(2).lower() == "x"
            node = nodo(m.group(3).strip(), checked)
            if cur is None:
                cur = {"name": "", "roots": []}
                secciones.append(cur)
                levels = []
            roots = cur["roots"]
            # clampa la profundidad a MAX_DEPTH
            depth = min(depth, MAX_DEPTH)
            # encontrar el padre más cercano disponible
            padre = None
            for d in range(depth - 1, -1, -1):
                if d < len(levels) and levels[d] is not None:
                    padre = levels[d]
                    break
            if padre is None:
                roots.append(node)
            else:
                padre["children"].append(node)
            # actualizar levels: este nodo pasa a ser el último de su profundidad
            while len(levels) <= depth:
                levels.append(None)
            levels[depth] = node
            # descartar niveles más profundos que el actual
            levels = levels[:depth + 1]
    if titulo is None:
        titulo = path.stem.replace("_", " ").replace("-", " ").title()
    return path, titulo, secciones


def escribir_nodo(lines, node, depth):
    marco = "x" if esta_completado(node) else " "
    indent = "  " * (depth - 1)
    lines.append(f"{indent}- [{marco}] {node['text']}")
    for c in node["children"]:
        escribir_nodo(lines, c, depth + 1)


def serializar(path, titulo, secciones):
    lineas = [f"# {titulo}"]
    for sec in secciones:
        if sec["name"]:
            lineas.append("")
            lineas.append(f"## {sec['name']}")
        for root in sec["roots"]:
            escribir_nodo(lineas, root, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def contar_pendientes(roots):
    n = 0
    for r in roots:
        n += contar_nodo(r)
    return n


def contar_nodo(node):
    if not node["children"]:
        return 0 if node["checked"] else 1
    return sum(contar_nodo(c) for c in node["children"])


# ---------------------------------------------------------------- modal -----

class InputModal(ModalScreen):
    """Modal genérico con una entrada de texto y confirmar/cancelar."""

    def __init__(self, titulo, placeholder="", boton="Añadir"):
        super().__init__()
        self._titulo = titulo
        self._placeholder = placeholder
        self._boton = boton

    def compose(self):
        yield Static(self._titulo, id="modal-title")
        yield Input(placeholder=self._placeholder, id="modal-input")
        with Horizontal(id="modal-buttons"):
            yield Button("Cancelar", variant="default", id="modal-cancel")
            yield Button(self._boton, variant="primary", id="modal-ok")

    def on_mount(self):
        self.query_one("#modal-input", Input).focus()

    def on_button_pressed(self, event):
        if event.button.id == "modal-ok":
            valor = self.query_one("#modal-input", Input).value.strip()
            self.dismiss(valor or None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event):
        valor = event.value.strip()
        self.dismiss(valor or None)


# -------------------------------------------------------------------- app ----

class ListaApp(App):
    TITLE = "Simple TO DO list"
    CSS = """
    Screen { background: #1e1e2e; }
    #main-view { margin: 1 2; color: #cdd6f4; height: auto; }
    #help { color: #6c7086; margin: 0 2 1 2; }
    VerticalScroll { height: 1fr; }
    #modal-title { color: #cdd6f4; padding: 0 1; }
    #modal-input { margin: 1 1; }
    #modal-buttons { padding: 0 1; }
    Footer { background: #45475a; color: #cdd6f4; }
    """

    BINDINGS = [
        Binding("up", "arriba", "↑", show=False),
        Binding("down", "abajo", "↓", show=False),
        Binding("k", "arriba", "↑", show=False),
        Binding("j", "abajo", "↓", show=False),
        Binding("space", "toggle", "Marcar", show=True),
        Binding("enter", "toggle", "Marcar", show=True),
        Binding("a", "anadir", "Sub-item", show=True),
        Binding("n", "nuevo", "Item", show=True),
        Binding("s", "seccion", "Sección", show=True),
        Binding("r", "renombrar", "Renombrar", show=True),
        Binding("x", "eliminar", "Eliminar", show=True),
        Binding("q", "salir", "Salir", show=True),
    ]

    def __init__(self, path, titulo, secciones):
        super().__init__()
        self._path = path
        self._titulo = titulo
        self._secciones = secciones
        self._cursor = 0  # índice global en flat
        self._flat = []   # lista de (si, path) donde path es tupla de índices
        self._lineas = []  # línea de render de cada item del flat (para scroll)

    def _reconstruir_flat(self):
        self._flat = []
        self._lineas = []
        for si, sec in enumerate(self._secciones):
            def walk(nodes, prefijo, linea):
                for i, node in enumerate(nodes):
                    p = prefijo + [i]
                    self._flat.append((si, tuple(p)))
                    self._lineas.append(linea)
                    walk(node["children"], p, linea + 1)
            walk(sec["roots"], [], 1)
        if self._flat and self._cursor >= len(self._flat):
            self._cursor = len(self._flat) - 1

    def _node(self, si, path):
        node = self._secciones[si]["roots"][path[0]]
        for idx in path[1:]:
            node = node["children"][idx]
        return node

    def compose(self):
        with VerticalScroll():
            yield Static(id="main-view")
        yield Static(id="help")
        yield Footer()

    def on_mount(self):
        self._reconstruir_flat()
        self._render()

    def _render(self):
        from rich.text import Text
        from rich.style import Style
        v = self.query_one("#main-view", Static)
        t = Text()
        t.append(self._titulo + "\n", style=Style(bold=True, color="#89b4fa"))
        linea = 1
        for si, sec in enumerate(self._secciones):
            if sec["name"]:
                t.append("\n" + sec["name"] + "\n",
                         style=Style(bold=True, color="#f9e2af"))
                linea += 2
            self._render_nodos(t, sec["roots"], 1, linea)
            linea += 1  # separación mínima entre secciones
        v.update(t)
        # scrollear al item seleccionado
        self.call_after_refresh(self._scroll_a_cursor)
        pend = sum(contar_pendientes(s["roots"]) for s in self._secciones)
        total = len(self._flat)
        ayuda = (f"j/k ↑↓ mover · espacio/enter marcar · a sub-item · n item · "
                 f"s sección · r renombrar · x eliminar · q salir    "
                 f"[{pend}/{total} pendientes]")
        self.query_one("#help", Static).update(ayuda)

    def _render_nodos(self, t, nodes, depth, base_linea):
        from rich.style import Style
        for i, node in enumerate(nodes):
            # buscar índice en flat para saber si está seleccionado
            idx = self._find_flat(node)
            sel = idx == self._cursor
            cb = "☑" if esta_completado(node) else "☐"
            cb_col = "#a6e3a1" if esta_completado(node) else "#6c7086"
            indent = "  " * (depth - 1)
            nom = node["text"]
            estilo = Style(color="#cdd6f4")
            if esta_completado(node):
                estilo = Style(color="#585b70", strike=True)
            if sel:
                estilo = Style(bold=True, color="#11111b",
                               bgcolor="#89b4fa", strike=esta_completado(node))
            t.append(("▸ " if sel else "  ") + indent + cb + " ",
                     style=Style(color=cb_col, bold=esta_completado(node)))
            t.append(nom, style=estilo)
            t.append("\n")
            self._render_nodos(t, node["children"], depth + 1, base_linea + i + 1)

    def _find_flat(self, node):
        """Devuelve el índice flat del nodo (búsqueda por identidad)."""
        for i, (si, path) in enumerate(self._flat):
            if self._node(si, path) is node:
                return i
        return -1

    def _guardar(self):
        serializar(self._path, self._titulo, self._secciones)

    def _scroll_a_cursor(self):
        """Lleva el item seleccionado a la zona visible del contenedor."""
        from textual.containers import VerticalScroll
        if not self._flat:
            return
        cont = self.query_one(VerticalScroll)
        linea = self._lineas[self._cursor]
        cont.scroll_to(y=linea, animate=False)

    # ----- acciones -----
    def action_arriba(self):
        if self._flat:
            self._cursor = (self._cursor - 1) % len(self._flat)
            self._render()

    def action_abajo(self):
        if self._flat:
            self._cursor = (self._cursor + 1) % len(self._flat)
            self._render()

    def action_toggle(self):
        if not self._flat:
            return
        si, path = self._flat[self._cursor]
        node = self._node(si, path)
        if node["children"]:
            # propagar: si todos completados -> desmarcar todo; si no -> marcar todo
            valor = not esta_completado(node)
            set_todos(node, valor)
        else:
            node["checked"] = not node["checked"]
        self._guardar()
        self._render()

    def _seccion_del_cursor(self):
        if self._flat:
            return self._flat[self._cursor][0]
        return len(self._secciones) - 1 if self._secciones else 0

    def _asegurar_seccion(self):
        si = self._seccion_del_cursor()
        if si < 0:
            si = 0
        if not self._secciones:
            self._secciones.append({"name": "", "roots": []})
            si = 0
        return si

    def action_anadir(self):
        """Añade un SUB-item al item seleccionado (un nivel más profundo)."""
        if self._flat:
            si, path = self._flat[self._cursor]
            depth = len(path)
            if depth >= MAX_DEPTH:
                self.notify(f"Límite de profundidad alcanzado ({MAX_DEPTH})",
                            severity="warning", timeout=3)
                return
        self._pide("Nuevo sub-item:", "Texto del sub-item", "Añadir",
                   lambda v: self._crear_sub(v))

    def _crear_sub(self, texto):
        if not texto:
            return
        si = self._asegurar_seccion()
        if self._flat:
            si, path = self._flat[self._cursor]
            node = self._node(si, path)
            node["children"].append(nodo(texto))
        else:
            self._secciones[si]["roots"].append(nodo(texto))
        self._reconstruir_flat()
        self._cursor = len(self._flat) - 1
        self._guardar()
        self._render()

    def action_nuevo(self):
        """Añade un item raíz (nivel 1) a la sección actual."""
        self._pide("Nuevo item:", "Texto del item", "Añadir",
                   lambda v: self._crear_root(v))

    def _crear_root(self, texto):
        if not texto:
            return
        si = self._asegurar_seccion()
        self._secciones[si]["roots"].append(nodo(texto))
        self._reconstruir_flat()
        self._cursor = len(self._flat) - 1
        self._guardar()
        self._render()

    def action_seccion(self):
        self._pide("Nueva sección:", "Nombre de la sección", "Crear",
                   lambda v: self._crear_seccion(v))

    def _crear_seccion(self, nombre):
        if not nombre:
            return
        self._secciones.append({"name": nombre, "roots": []})
        self._guardar()
        self._render()

    def action_renombrar(self):
        si = self._seccion_del_cursor()
        if si < 0:
            return
        actual = self._secciones[si]["name"] or "General"
        self._pide("Renombrar sección:", actual, "Guardar",
                   lambda v: self._renombrar(si, v))

    def _renombrar(self, si, nombre):
        if nombre:
            self._secciones[si]["name"] = nombre
            self._guardar()
            self._render()

    def action_eliminar(self):
        if not self._flat:
            return
        si, path = self._flat[self._cursor]
        sec = self._secciones[si]
        if len(path) == 1:
            del sec["roots"][path[0]]
        else:
            padre = self._node(si, path[:-1])
            del padre["children"][path[-1]]
        self._reconstruir_flat()
        if self._flat and self._cursor >= len(self._flat):
            self._cursor = len(self._flat) - 1
        self._guardar()
        self._render()

    def action_salir(self):
        self._guardar()
        self.exit()

    def _pide(self, titulo, placeholder, boton, callback):
        modal = InputModal(titulo, placeholder, boton)
        self.push_screen(modal, callback)


# ---------------------------------------------------------------- CLI --------

def cmd_ver(ruta):
    path, titulo, secciones = leer_lista(Path(ruta))
    print(f"# {titulo}")
    for sec in secciones:
        if sec["name"]:
            print(f"## {sec['name']}")
        for root in sec["roots"]:
            ver_nodo(root, 1)
    pend = sum(contar_pendientes(s["roots"]) for s in secciones)
    print(f"\n({pend} pendientes)")


def ver_nodo(node, depth):
    marco = "x" if esta_completado(node) else " "
    indent = "  " * (depth - 1)
    print(f"{indent}- [{marco}] {node['text']}")
    for c in node["children"]:
        ver_nodo(c, depth + 1)


def cmd_secciones(ruta):
    path, titulo, secciones = leer_lista(Path(ruta))
    print(f"# {titulo}")
    for sec in secciones:
        total = len(sec["roots"])
        pend = contar_pendientes(sec["roots"])
        nombre = sec["name"] or "General"
        print(f"## {nombre}  [{pend}/{total} pendientes]")


def main():
    args = sys.argv[1:]
    if not args:
        print("Uso: lista <ruta>   |   lista ver <ruta>   |   lista secciones <ruta>")
        sys.exit(1)
    if args[0] == "ver":
        if len(args) < 2:
            sys.exit("lista ver: falta la ruta")
        cmd_ver(args[1])
        return
    if args[0] == "secciones":
        if len(args) < 2:
            sys.exit("lista secciones: falta la ruta")
        cmd_secciones(args[1])
        return
    r = args[0]
    if r in (".",):
        r = os.getcwd()
    path = Path(r)
    if path.is_dir():
        path = path / f"{path.name}.md"
    path = path.expanduser()
    p, titulo, secciones = leer_lista(path)
    ListaApp(p, titulo, secciones).run()


if __name__ == "__main__":
    main()
