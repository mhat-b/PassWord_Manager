"""Tema visual centralizado: colores, fuentes y estilos ttk."""

from tkinter import ttk

# Paleta
BG = "#161B29"            # fondo general (azul muy oscuro)
BG_PANEL = "#1F2740"       # paneles / tarjetas
BG_INPUT = "#26304D"       # campos de entrada
ACCENT = "#7C5CFF"         # violeta acento (marca)
ACCENT_HOVER = "#9478FF"
DANGER = "#FF5C7A"
DANGER_HOVER = "#FF7C93"
SUCCESS = "#3DDC97"
TEXT = "#EDEEF7"
TEXT_MUTED = "#8B93B8"
BORDER = "#323C5E"
ROW_ALT = "#1B2338"

FONT_FAMILY = "Segoe UI"


def apply_theme(root) -> None:
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BG, foreground=TEXT, font=(FONT_FAMILY, 10))

    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=BG_PANEL)
    style.configure("PanelTitle.TLabel", background=BG_PANEL, foreground=TEXT,
                     font=(FONT_FAMILY, 15, "bold"))
    style.configure("PanelLabel.TLabel", background=BG_PANEL, foreground=TEXT_MUTED,
                     font=(FONT_FAMILY, 10))

    style.configure("TLabel", background=BG, foreground=TEXT, font=(FONT_FAMILY, 10))
    style.configure("Title.TLabel", background=BG, foreground=TEXT,
                     font=(FONT_FAMILY, 20, "bold"))
    style.configure("Subtitle.TLabel", background=BG, foreground=TEXT_MUTED,
                     font=(FONT_FAMILY, 10))
    style.configure("Muted.TLabel", background=BG, foreground=TEXT_MUTED,
                     font=(FONT_FAMILY, 9))
    style.configure("ErrorStatus.TLabel", background=BG, foreground=DANGER,
                     font=(FONT_FAMILY, 9, "bold"))
    style.configure("OkStatus.TLabel", background=BG, foreground=SUCCESS,
                     font=(FONT_FAMILY, 9, "bold"))
    style.configure("PanelError.TLabel", background=BG_PANEL, foreground=DANGER,
                     font=(FONT_FAMILY, 9, "bold"))
    style.configure("PanelOk.TLabel", background=BG_PANEL, foreground=SUCCESS,
                     font=(FONT_FAMILY, 9, "bold"))
    style.configure("PanelEmoji.TLabel", background=BG_PANEL, foreground=ACCENT,
                     font=(FONT_FAMILY, 28))

    # Entradas de texto
    style.configure(
        "TEntry",
        fieldbackground=BG_INPUT,
        background=BG_INPUT,
        foreground=TEXT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        insertcolor=TEXT,
        padding=6,
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT)])

    # Botón primario (acento violeta)
    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="#FFFFFF",
        borderwidth=0,
        focusthickness=0,
        padding=(14, 8),
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.map("Accent.TButton", background=[("active", ACCENT_HOVER), ("pressed", ACCENT_HOVER)])

    # Botón neutro
    style.configure(
        "Ghost.TButton",
        background=BG_PANEL,
        foreground=TEXT,
        borderwidth=1,
        bordercolor=BORDER,
        focusthickness=0,
        padding=(12, 7),
        font=(FONT_FAMILY, 10),
    )
    style.map(
        "Ghost.TButton",
        background=[("active", BG_INPUT)],
        bordercolor=[("active", ACCENT)],
    )

    # Botón peligro (eliminar / bloquear)
    style.configure(
        "Danger.TButton",
        background=DANGER,
        foreground="#FFFFFF",
        borderwidth=0,
        focusthickness=0,
        padding=(12, 7),
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.map("Danger.TButton", background=[("active", DANGER_HOVER)])

    # Checkbutton
    style.configure("TCheckbutton", background=BG, foreground=TEXT)
    style.map("TCheckbutton", background=[("active", BG)])

    # Treeview (tabla)
    style.configure(
        "Treeview",
        background=BG_PANEL,
        fieldbackground=BG_PANEL,
        foreground=TEXT,
        bordercolor=BORDER,
        borderwidth=0,
        rowheight=30,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "Treeview.Heading",
        background=BG_INPUT,
        foreground=TEXT_MUTED,
        borderwidth=0,
        font=(FONT_FAMILY, 9, "bold"),
        padding=(8, 8),
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#FFFFFF")],
    )
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    # Scrollbar fina y minimalista (sin flechas, solo el "thumb")
    style.element_create("Slim.Vertical.Scrollbar.trough", "from", "clam")
    style.element_create("Slim.Vertical.Scrollbar.thumb", "from", "clam")
    style.layout(
        "Slim.Vertical.TScrollbar",
        [
            (
                "Slim.Vertical.Scrollbar.trough",
                {
                    "sticky": "ns",
                    "children": [
                        (
                            "Slim.Vertical.Scrollbar.thumb",
                            {"expand": 1, "sticky": "nswe"},
                        )
                    ],
                },
            )
        ],
    )
    style.configure(
        "Slim.Vertical.TScrollbar",
        troughcolor=BG_PANEL,
        background=BORDER,
        bordercolor=BG_PANEL,
        lightcolor=BORDER,
        darkcolor=BORDER,
        relief="flat",
        gripcount=0,
        width=8,
    )
    style.map(
        "Slim.Vertical.TScrollbar",
        background=[("active", ACCENT), ("!active", BORDER)],
    )
