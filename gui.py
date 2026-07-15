"""Interfaz gráfica del gestor de contraseñas (Tkinter + ttk.Treeview)."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from theme import BG, BG_PANEL, ROW_ALT, TEXT_MUTED, apply_theme
from core import PasswordManager
from exceptions import (
    AuthenticationError,
    DuplicateEntryError,
    EntryNotFoundError,
    PasswordManagerError,
    VaultCorruptedError,
    VaultExistsError,
    VaultNotFoundError,
)
from models import PasswordEntry
from vault import PasswordVault

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

DEFAULT_VAULT_NAME = "vault.dat"


class EntryDialog(tk.Toplevel):
    """Formulario modal para crear o editar una entrada."""

    def __init__(self, parent, title: str, initial: PasswordEntry | None = None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.result: dict | None = None

        container = ttk.Frame(self, style="Panel.TFrame", padding=20)
        container.pack(fill="both", expand=True, padx=14, pady=14)

        ttk.Label(container, text=title, style="PanelTitle.TLabel").grid(
            row=0, column=0, columnspan=5, sticky="w", pady=(0, 14)
        )

        fields = [
            ("service", "Servicio"),
            ("username", "Usuario"),
            ("password", "Contraseña"),
            ("url", "URL"),
            ("notes", "Notas"),
        ]
        self._vars: dict[str, tk.StringVar] = {}

        for offset, (key, label) in enumerate(fields):
            row = offset + 1
            lbl = ttk.Label(container, text=label + ":", style="PanelLabel.TLabel")
            lbl.grid(row=row, column=0, sticky="e", padx=(0, 8), pady=6)
            initial_value = getattr(initial, key, "") if initial else ""
            var = tk.StringVar(value=initial_value)
            self._vars[key] = var
            show = "*" if key == "password" else ""
            entry_widget = ttk.Entry(container, textvariable=var, width=32, show=show)
            entry_widget.grid(row=row, column=1, padx=4, pady=6, columnspan=2, sticky="w")
            if key == "password":
                self._pw_entry_widget = entry_widget

        gen_btn = ttk.Button(container, text="Generar", style="Ghost.TButton", command=self._generate)
        gen_btn.grid(row=3, column=3, padx=(6, 0))

        show_var = tk.BooleanVar(value=False)

        def toggle():
            self._pw_entry_widget.config(show="" if show_var.get() else "*")

        ttk.Checkbutton(container, text="Mostrar", variable=show_var, command=toggle).grid(
            row=3, column=4, sticky="w", padx=(6, 0)
        )

        btn_frame = ttk.Frame(container, style="Panel.TFrame")
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=5, pady=(16, 0), sticky="e")
        ttk.Button(btn_frame, text="Cancelar", style="Ghost.TButton", command=self.destroy).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(btn_frame, text="Guardar", style="Accent.TButton", command=self._on_save).pack(
            side="left"
        )

        self.bind("<Return>", lambda _e: self._on_save())
        self.bind("<Escape>", lambda _e: self.destroy())
        self.wait_window(self)

    def _generate(self) -> None:
        pwd = PasswordManager.generate_password(length=16)
        self._vars["password"].set(pwd)

    def _on_save(self) -> None:
        service = self._vars["service"].get().strip()
        username = self._vars["username"].get().strip()
        password = self._vars["password"].get()

        if not service or not username or not password:
            messagebox.showerror("Datos incompletos", "Servicio, usuario y contraseña son obligatorios.", parent=self)
            return

        self.result = {k: v.get() for k, v in self._vars.items()}
        self.destroy()


class LoginFrame(ttk.Frame):
    """Pantalla inicial: elegir/crear archivo de bóveda y desbloquear."""

    def __init__(self, master, on_unlocked):
        super().__init__(master, padding=0)
        self.on_unlocked = on_unlocked
        self.vault_path = tk.StringVar(value=str(Path.cwd() / DEFAULT_VAULT_NAME))

        # Centra una tarjeta en medio de la ventana
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, style="Panel.TFrame", padding=32)
        card.grid(row=0, column=0)

        ttk.Label(card, text="🔒", style="PanelEmoji.TLabel").grid(
            row=0, column=0, columnspan=3, pady=(0, 4)
        )
        ttk.Label(card, text="Gestor de Contraseñas", style="PanelTitle.TLabel").grid(
            row=1, column=0, columnspan=3, pady=(0, 2)
        )
        ttk.Label(card, text="Desbloquea tu bóveda o crea una nueva", style="PanelLabel.TLabel").grid(
            row=2, column=0, columnspan=3, pady=(0, 20)
        )

        ttk.Label(card, text="Archivo de bóveda", style="PanelLabel.TLabel").grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(0, 4)
        )
        ttk.Entry(card, textvariable=self.vault_path, width=36).grid(
            row=4, column=0, columnspan=2, sticky="we"
        )
        ttk.Button(card, text="...", style="Ghost.TButton", width=3, command=self._browse).grid(
            row=4, column=2, padx=(6, 0)
        )

        ttk.Label(card, text="Contraseña maestra", style="PanelLabel.TLabel").grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(14, 4)
        )
        self.master_pw = tk.StringVar()
        pw_entry = ttk.Entry(card, textvariable=self.master_pw, show="*", width=36)
        pw_entry.grid(row=6, column=0, columnspan=3, sticky="we")
        pw_entry.bind("<Return>", lambda _e: self._unlock())
        pw_entry.focus_set()

        btn_frame = ttk.Frame(card, style="Panel.TFrame")
        btn_frame.grid(row=7, column=0, columnspan=3, pady=(20, 0), sticky="we")
        ttk.Button(btn_frame, text="Crear bóveda nueva", style="Ghost.TButton",
                   command=self._create).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Desbloquear", style="Accent.TButton",
                   command=self._unlock).pack(side="left")

        self.status = ttk.Label(card, text="", style="PanelError.TLabel")
        self.status.grid(row=8, column=0, columnspan=3, pady=(14, 0), sticky="w")

    def _browse(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Archivo de bóveda",
            defaultextension=".dat",
            initialfile=DEFAULT_VAULT_NAME,
            filetypes=[("Bóveda cifrada", "*.dat"), ("Todos los archivos", "*.*")],
        )
        if path:
            self.vault_path.set(path)

    def _create(self) -> None:
        vault = PasswordVault(self.vault_path.get())
        pw = self.master_pw.get()
        if not pw:
            self.status.config(text="Escribe una contraseña maestra.")
            return
        try:
            vault.create(pw)
        except VaultExistsError as exc:
            self.status.config(text=str(exc))
            return
        except PasswordManagerError as exc:
            self.status.config(text=str(exc))
            return
        self.status.config(text="")
        self.on_unlocked(vault)

    def _unlock(self) -> None:
        vault = PasswordVault(self.vault_path.get())
        pw = self.master_pw.get()
        try:
            vault.unlock(pw)
        except (VaultNotFoundError, AuthenticationError, VaultCorruptedError) as exc:
            self.status.config(text=str(exc))
            return
        self.status.config(text="")
        self.on_unlocked(vault)


class VaultFrame(ttk.Frame):
    """Pantalla principal: Treeview con las entradas y acciones CRUD."""

    COLUMNS = ("service", "username", "url", "updated_at")
    HEADERS = {"service": "Servicio", "username": "Usuario", "url": "URL", "updated_at": "Actualizado"}

    def __init__(self, master, vault: PasswordVault, on_locked):
        super().__init__(master, padding=(20, 16))
        self.vault = vault
        self.manager = PasswordManager(vault)
        self.on_locked = on_locked

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 14))
        ttk.Label(header, text="🔒 Centro de Contraseñas", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Bloquear", style="Danger.TButton", command=self._lock).pack(side="right")

        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", pady=(0, 12))
        top_bar.columnconfigure(0, weight=1)
        top_bar.columnconfigure(1, weight=0)

        search_area = ttk.Frame(top_bar)
        search_area.grid(row=0, column=0, sticky="w")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh())
        ttk.Entry(search_area, textvariable=self.search_var, width=26).pack(side="left")
        ttk.Label(search_area, text="🔍 buscar", style="Muted.TLabel").pack(side="left", padx=(8, 0))

        btn_area = ttk.Frame(top_bar)
        btn_area.grid(row=0, column=1, sticky="e")

        ttk.Button(btn_area, text="Editar", style="Ghost.TButton", command=self._edit).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_area, text="Eliminar", style="Ghost.TButton", command=self._delete).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_area, text="Ver / Copiar", style="Ghost.TButton", command=self._reveal).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(btn_area, text="+ Agregar", style="Accent.TButton", command=self._add).pack(
            side="left"
        )

        tree_frame = ttk.Frame(self, style="Panel.TFrame", padding=1)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=self.COLUMNS, show="headings", selectmode="browse")
        for col in self.COLUMNS:
            self.tree.heading(col, text=self.HEADERS[col])
            self.tree.column(col, width=150, minwidth=150, stretch=False, anchor="w")
        self.tree.column("updated_at", width=150, minwidth=150)
        self.tree.tag_configure("odd", background=ROW_ALT)
        self.tree.tag_configure("even", background=BG_PANEL)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _e: self._edit())
        # bloquea el arrastre para redimensionar columnas (clic sobre el separador de encabezado)
        self.tree.bind("<Button-1>", self._block_column_resize, add="+")

        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", style="Slim.Vertical.TScrollbar", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.status = ttk.Label(self, text="", style="OkStatus.TLabel")
        self.status.pack(fill="x", pady=(10, 0))

        self._refresh()

    def _block_column_resize(self, event) -> str | None:
        """Evita que el usuario achique/agrande las columnas arrastrando el borde."""
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"
        return None

    def _set_status(self, text: str, error: bool = False) -> None:
        self.status.config(text=text, style="ErrorStatus.TLabel" if error else "OkStatus.TLabel")

    def _refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        query = self.search_var.get()
        try:
            entries = self.vault.search(query) if query else self.vault.list_entries()
        except AuthenticationError:
            return
        for i, entry in enumerate(entries):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert(
                "", "end", iid=entry.id,
                values=(entry.service, entry.username, entry.url, entry.updated_at),
                tags=(tag,),
            )

    def _selected_id(self) -> str | None:
        selection = self.tree.selection()
        return selection[0] if selection else None

    def _add(self) -> None:
        dialog = EntryDialog(self, "Nueva entrada")
        if dialog.result is None:
            return
        entry = PasswordEntry(**dialog.result)
        try:
            self.vault.add_entry(entry)
        except DuplicateEntryError as exc:
            messagebox.showerror("Duplicado", str(exc))
            return
        self._set_status(f"Entrada '{entry.service}' agregada.")
        self._refresh()

    def _edit(self) -> None:
        entry_id = self._selected_id()
        if entry_id is None:
            messagebox.showinfo("Sin selección", "Selecciona una entrada primero.")
            return
        try:
            current = self.vault.get_entry(entry_id)
        except EntryNotFoundError as exc:
            messagebox.showerror("Error", str(exc))
            return
        dialog = EntryDialog(self, "Editar entrada", initial=current)
        if dialog.result is None:
            return
        try:
            self.vault.update_entry(entry_id, **dialog.result)
        except EntryNotFoundError as exc:
            messagebox.showerror("Error", str(exc))
            return
        self._set_status(f"Entrada '{dialog.result['service']}' actualizada.")
        self._refresh()

    def _delete(self) -> None:
        entry_id = self._selected_id()
        if entry_id is None:
            messagebox.showinfo("Sin selección", "Selecciona una entrada primero.")
            return
        service = self.tree.item(entry_id, "values")[0]
        if not messagebox.askyesno("Confirmar", f"¿Eliminar la entrada de '{service}'?"):
            return
        try:
            self.vault.delete_entry(entry_id)
        except EntryNotFoundError as exc:
            messagebox.showerror("Error", str(exc))
            return
        self._set_status(f"Entrada '{service}' eliminada.")
        self._refresh()

    def _reveal(self) -> None:
        entry_id = self._selected_id()
        if entry_id is None:
            messagebox.showinfo("Sin selección", "Selecciona una entrada primero.")
            return
        try:
            entry = self.vault.get_entry(entry_id)
        except EntryNotFoundError as exc:
            messagebox.showerror("Error", str(exc))
            return
        self.clipboard_clear()
        self.clipboard_append(entry.password)
        strength = self.manager.evaluate_strength(entry.password)
        messagebox.showinfo(
            "Contraseña copiada",
            f"Servicio: {entry.service}\nUsuario: {entry.username}\nFuerza: {strength}\n\n"
            "La contraseña se copió al portapapeles.",
        )

    def _lock(self) -> None:
        self.vault.lock()
        self.on_locked()


class App(tk.Tk):
    """Ventana raíz: cambia entre LoginFrame y VaultFrame."""

    def __init__(self):
        super().__init__()
        self.title("Gestor de Contraseñas")
        self.geometry("820x520")
        self.minsize(780, 420)
        apply_theme(self)
        self._apply_icon()
        self._current: ttk.Frame | None = None
        self._show_login()

    def _apply_icon(self) -> None:
        ico_path = ASSETS_DIR / "icon.ico"
        png_path = ASSETS_DIR / "icon.png"
        try:
            if ico_path.exists():
                self.iconbitmap(str(ico_path))  # barra de título / taskbar en Windows
            if png_path.exists():
                self._icon_img = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, self._icon_img)  # multiplataforma (Linux/Mac)
        except tk.TclError:
            pass  # si el formato no es compatible con esta plataforma, seguimos sin ícono

    def _clear(self) -> None:
        if self._current is not None:
            self._current.destroy()
            self._current = None

    def _show_login(self) -> None:
        self._clear()
        self._current = LoginFrame(self, on_unlocked=self._show_vault)
        self._current.pack(fill="both", expand=True)

    def _show_vault(self, vault: PasswordVault) -> None:
        self._clear()
        self._current = VaultFrame(self, vault, on_locked=self._show_login)
        self._current.pack(fill="both", expand=True)


def run() -> None:
    app = App()
    app.mainloop()
