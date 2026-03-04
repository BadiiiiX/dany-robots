"""
Utilitaires graphiques partagés entre les écrans.
Centralise les couleurs, polices et composants réutilisables (boutons, barres, listes).
"""
from __future__ import annotations

import pygame

# ------------------------------------------------------------------
# Palette
# ------------------------------------------------------------------

# Fond général
C_BG         = (15,  15,  30)
C_PANEL      = (25,  25,  50)
C_PANEL_DARK = (10,  10,  20)

# Texte
C_WHITE      = (240, 240, 255)
C_GREY       = (160, 160, 180)
C_GREY_DARK  = (80,   80, 100)

# Accents
C_ACCENT     = (80,  140, 255)
C_ACCENT_HOV = (110, 170, 255)
C_DANGER     = (220,  60,  60)
C_DANGER_HOV = (255,  90,  90)
C_SUCCESS    = (60,  200, 100)
C_WARNING    = (230, 180,  40)
C_DISABLED   = (60,   60,  80)

# Barres
C_HP_BAR     = (50,  200,  80)
C_HP_LOW     = (220,  60,  60)
C_HP_MED     = (220, 180,  40)
C_ENERGY_BAR = (80,  160, 255)
C_BAR_BG     = (30,   30,  50)

# Contour sélection
C_SELECTED   = (255, 220,  40)
C_BORDER     = (50,   50,  80)

# Type couleurs
TYPE_COLORS = {
    "ASSAULT":  (220,  60,  60),
    "DEFENDER": (60,  120, 220),
    "AGILE":    (60,  200, 120),
    "BALANCE":  (200, 150,  50),
}

# ------------------------------------------------------------------
# Polices (initialisées une fois)
# ------------------------------------------------------------------

_fonts: dict[tuple[str | None, int, bool], pygame.font.Font] = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Retourne une police mise en cache."""
    key = (None, size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("segoeui", size, bold=bold)
    return _fonts[key]


# ------------------------------------------------------------------
# Composant Button
# ------------------------------------------------------------------

class Button:
    """Bouton rectangulaire cliquable avec survol et état désactivé."""

    def __init__(
        self,
        rect: tuple[int, int, int, int],
        label: str,
        color: tuple[int, int, int] = C_ACCENT,
        hover_color: tuple[int, int, int] | None = None,
        text_color: tuple[int, int, int] = C_WHITE,
        font_size: int = 22,
        border_radius: int = 8,
        enabled: bool = True,
    ):
        self.rect         = pygame.Rect(rect)
        self.label        = label
        self.color        = color
        self.hover_color  = hover_color or _lighten(color, 30)
        self.text_color   = text_color
        self.font_size    = font_size
        self.border_radius = border_radius
        self.enabled      = enabled
        self._hovered     = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Retourne True si le bouton a été cliqué."""
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def update_hover(self, mouse_pos: tuple[int, int]) -> None:
        self._hovered = self.rect.collidepoint(mouse_pos)

    def render(self, surface: pygame.Surface) -> None:
        if not self.enabled:
            color = C_DISABLED
        elif self._hovered:
            color = self.hover_color
        else:
            color = self.color

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        # Bordure subtile
        pygame.draw.rect(surface, C_BORDER, self.rect, width=1, border_radius=self.border_radius)

        font  = get_font(self.font_size, bold=True)
        text  = font.render(self.label, True, self.text_color if self.enabled else C_GREY_DARK)
        trect = text.get_rect(center=self.rect.center)
        surface.blit(text, trect)


# ------------------------------------------------------------------
# Composant Slider
# ------------------------------------------------------------------

class Slider:
    """
    Curseur horizontal permettant de sélectionner une valeur entière dans [min_val, max_val].
    """

    BAR_H     = 8
    KNOB_R    = 10

    def __init__(
        self,
        x: int, y: int, width: int,
        min_val: int, max_val: int,
        value: int,
        label: str = "",
        color: tuple[int, int, int] = C_ACCENT,
    ):
        self.x        = x
        self.y        = y
        self.width    = width
        self.min_val  = min_val
        self.max_val  = max_val
        self.value    = max(min_val, min(max_val, value))
        self.label    = label
        self.color    = color
        self._dragging = False

    # Position du curseur en pixels
    def _knob_x(self) -> int:
        ratio = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
        return int(self.x + ratio * self.width)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Retourne True si la valeur a changé."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            kx = self._knob_x()
            dist = abs(event.pos[0] - kx) + abs(event.pos[1] - (self.y + self.BAR_H // 2))
            bar_rect = pygame.Rect(self.x, self.y - self.KNOB_R, self.width, self.KNOB_R * 2 + self.BAR_H)
            if dist <= self.KNOB_R + 8 or bar_rect.collidepoint(event.pos):
                self._dragging = True
                return self._update_from_mouse(event.pos[0])
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
        if event.type == pygame.MOUSEMOTION and self._dragging:
            return self._update_from_mouse(event.pos[0])
        return False

    def _update_from_mouse(self, mx: int) -> bool:
        ratio = max(0.0, min(1.0, (mx - self.x) / max(1, self.width)))
        new_val = round(self.min_val + ratio * (self.max_val - self.min_val))
        if new_val != self.value:
            self.value = new_val
            return True
        return False

    def render(self, surface: pygame.Surface) -> None:
        bar_y = self.y
        # Piste de fond
        pygame.draw.rect(surface, C_BAR_BG,
                         pygame.Rect(self.x, bar_y, self.width, self.BAR_H),
                         border_radius=4)
        # Partie remplie
        filled = self._knob_x() - self.x
        if filled > 0:
            pygame.draw.rect(surface, self.color,
                             pygame.Rect(self.x, bar_y, filled, self.BAR_H),
                             border_radius=4)
        # Curseur
        kx = self._knob_x()
        ky = bar_y + self.BAR_H // 2
        pygame.draw.circle(surface, C_WHITE, (kx, ky), self.KNOB_R)
        pygame.draw.circle(surface, self.color, (kx, ky), self.KNOB_R - 3)

        # Étiquette
        if self.label:
            font  = get_font(18)
            lbl   = font.render(f"{self.label}: {self.value}", True, C_WHITE)
            surface.blit(lbl, (self.x, bar_y - 22))


# ------------------------------------------------------------------
# Composant TextInput
# ------------------------------------------------------------------

class TextInput:
    """Champ de saisie de texte monoligne."""

    def __init__(
        self,
        rect: tuple[int, int, int, int],
        placeholder: str = "",
        max_length: int = 20,
        font_size: int = 22,
    ):
        self.rect        = pygame.Rect(rect)
        self.placeholder = placeholder
        self.max_length  = max_length
        self.font_size   = font_size
        self.text        = ""
        self.active      = False
        self._cursor_vis = True
        self._cursor_timer = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Retourne True si le texte a changé."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.text:
                    self.text = self.text[:-1]
                    return True
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                self.active = False
            elif len(self.text) < self.max_length:
                if event.unicode.isprintable():
                    self.text += event.unicode
                    return True
        return False

    def render(self, surface: pygame.Surface, dt_ms: int = 33) -> None:
        border_color = C_ACCENT if self.active else C_BORDER
        pygame.draw.rect(surface, C_PANEL_DARK, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=6)

        font = get_font(self.font_size)
        if self.text:
            txt = font.render(self.text, True, C_WHITE)
        else:
            txt = font.render(self.placeholder, True, C_GREY_DARK)

        # Curseur clignotant
        self._cursor_timer += dt_ms
        if self._cursor_timer >= 500:
            self._cursor_timer = 0
            self._cursor_vis = not self._cursor_vis

        surface.blit(txt, (self.rect.x + 10, self.rect.centery - txt.get_height() // 2))
        if self.active and self._cursor_vis and self.text:
            cx = self.rect.x + 10 + txt.get_width() + 2
            cy = self.rect.centery - txt.get_height() // 2
            pygame.draw.line(surface, C_WHITE, (cx, cy), (cx, cy + txt.get_height()), 2)


# ------------------------------------------------------------------
# Composant Dropdown
# ------------------------------------------------------------------

class Dropdown:
    """Liste déroulante simple."""

    ITEM_H = 34

    def __init__(
        self,
        rect: tuple[int, int, int, int],
        options: list[str],
        selected_index: int = 0,
        font_size: int = 20,
    ):
        self.rect           = pygame.Rect(rect)
        self.options        = options
        self.selected_index = max(0, min(selected_index, len(options) - 1))
        self.font_size      = font_size
        self.open           = False

    @property
    def selected(self) -> str:
        return self.options[self.selected_index] if self.options else ""

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Retourne True si la sélection a changé."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
                return False
            if self.open:
                for i in range(len(self.options)):
                    item_rect = self._item_rect(i)
                    if item_rect.collidepoint(event.pos):
                        old = self.selected_index
                        self.selected_index = i
                        self.open = False
                        return self.selected_index != old
                self.open = False
        return False

    def _item_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(
            self.rect.x,
            self.rect.bottom + index * self.ITEM_H,
            self.rect.width,
            self.ITEM_H,
        )

    def render(self, surface: pygame.Surface) -> None:
        # Bouton principal
        pygame.draw.rect(surface, C_PANEL, self.rect, border_radius=6)
        pygame.draw.rect(surface, C_ACCENT if self.open else C_BORDER, self.rect, width=2, border_radius=6)

        font = get_font(self.font_size)
        lbl  = font.render(self.selected, True, C_WHITE)
        surface.blit(lbl, (self.rect.x + 10, self.rect.centery - lbl.get_height() // 2))

        # Flèche
        arrow = font.render("v" if not self.open else "^", True, C_GREY)
        surface.blit(arrow, (self.rect.right - 26, self.rect.centery - arrow.get_height() // 2))

        if self.open:
            for i, opt in enumerate(self.options):
                ir = self._item_rect(i)
                bg = C_ACCENT if i == self.selected_index else C_PANEL_DARK
                pygame.draw.rect(surface, bg, ir)
                pygame.draw.rect(surface, C_BORDER, ir, width=1)
                item_lbl = font.render(opt, True, C_WHITE)
                surface.blit(item_lbl, (ir.x + 10, ir.centery - item_lbl.get_height() // 2))


# ------------------------------------------------------------------
# Fonctions utilitaires
# ------------------------------------------------------------------

def draw_bar(
    surface: pygame.Surface,
    rect: tuple[int, int, int, int],
    value: float,
    max_value: float,
    color: tuple[int, int, int],
    bg_color: tuple[int, int, int] = C_BAR_BG,
    border_radius: int = 4,
) -> None:
    """Dessine une barre de progression."""
    r = pygame.Rect(rect)
    pygame.draw.rect(surface, bg_color, r, border_radius=border_radius)
    ratio = max(0.0, min(1.0, value / max_value)) if max_value > 0 else 0.0
    if ratio > 0:
        fill_rect = pygame.Rect(r.x, r.y, int(r.width * ratio), r.height)
        pygame.draw.rect(surface, color, fill_rect, border_radius=border_radius)
    pygame.draw.rect(surface, C_BORDER, r, width=1, border_radius=border_radius)


def hp_color(hp: float, max_hp: float) -> tuple[int, int, int]:
    """Retourne la couleur de la barre de PV selon le ratio restant."""
    ratio = hp / max_hp if max_hp > 0 else 0
    if ratio > 0.5:
        return C_HP_BAR
    if ratio > 0.25:
        return C_HP_MED
    return C_HP_LOW


def draw_text_centered(
    surface: pygame.Surface,
    text: str,
    cx: int, cy: int,
    size: int = 22,
    bold: bool = False,
    color: tuple[int, int, int] = C_WHITE,
) -> None:
    font = get_font(size, bold=bold)
    surf = font.render(text, True, color)
    surface.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))


def draw_text(
    surface: pygame.Surface,
    text: str,
    x: int, y: int,
    size: int = 20,
    bold: bool = False,
    color: tuple[int, int, int] = C_WHITE,
) -> int:
    """Dessine du texte et retourne la hauteur de la ligne."""
    font = get_font(size, bold=bold)
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))
    return surf.get_height()


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """Découpe une chaîne en lignes qui tiennent dans max_width pixels."""
    words  = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _lighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(min(255, c + amount) for c in color)  # type: ignore
