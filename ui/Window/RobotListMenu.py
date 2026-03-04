"""
Écran liste des robots.
Affiche une grille de cartes (nom, type, stats), suppression avec confirmation, retour.
"""
from __future__ import annotations

import pygame
from ui.Window.Window import Window
from ui import ui_helpers as ui
from impl.sauvegarde import charger_robots, sauvegarder_robots
from impl.Robot.Robot import Robot

_CARD_W = 260
_CARD_H = 180
_COLS   = 4
_GAP    = 18
_TOP_Y  = 120


class RobotListMenu(Window):
    """Écran de liste des robots sauvegardés."""

    def __init__(self, robot_ui):
        super().__init__(robot_ui)
        self._robots:       list[Robot]      = []
        self._confirm_idx:  int | None       = None   # index du robot à supprimer
        self._scroll_y:     int              = 0
        self._btn_back:     ui.Button | None = None
        self._btn_confirm:  ui.Button | None = None
        self._btn_cancel:   ui.Button | None = None

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self._robots     = charger_robots()
        self._confirm_idx = None
        self._scroll_y    = 0
        w, h = self.ui.screen.get_size()
        self._btn_back = ui.Button(
            (40, h - 60, 130, 40), "< Retour",
            color=ui.C_DANGER, hover_color=ui.C_DANGER_HOV, font_size=18,
        )
        # Boutons de la boîte de confirmation (positionnés dynamiquement)
        self._btn_confirm = ui.Button((0, 0, 150, 44), "Supprimer",
                                      color=ui.C_DANGER, hover_color=ui.C_DANGER_HOV)
        self._btn_cancel  = ui.Button((0, 0, 150, 44), "Annuler",
                                      color=ui.C_ACCENT, hover_color=ui.C_ACCENT_HOV)

    # ------------------------------------------------------------------
    # Événements
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        assert self._btn_back

        # Boîte de confirmation ouverte → seuls ces boutons sont actifs
        if self._confirm_idx is not None:
            if self._btn_confirm and self._btn_confirm.handle_event(event):
                self._delete_robot(self._confirm_idx)
                self._confirm_idx = None
            if self._btn_cancel and self._btn_cancel.handle_event(event):
                self._confirm_idx = None
            return

        if self._btn_back.handle_event(event):
            from ui.Window.Menu import Menu
            self.ui.set_window(Menu(self.ui))
            return

        # Scroll molette
        if event.type == pygame.MOUSEWHEEL:
            self._scroll_y = max(0, self._scroll_y - event.y * 30)

        # Clic sur bouton Supprimer d'une carte
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn in enumerate(self._delete_buttons()):
                if btn.rect.collidepoint(event.pos):
                    self._confirm_idx = i
                    return

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        if self._btn_back:
            self._btn_back.update_hover(mouse_pos)
        if self._confirm_idx is not None:
            if self._btn_confirm:
                self._btn_confirm.update_hover(mouse_pos)
            if self._btn_cancel:
                self._btn_cancel.update_hover(mouse_pos)

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> None:
        surface = self.ui.screen
        w, h    = surface.get_size()
        surface.fill(ui.C_BG)

        ui.draw_text_centered(surface, "MES ROBOTS", w // 2, 55, size=40, bold=True)

        if not self._robots:
            ui.draw_text_centered(surface, "Aucun robot disponible",
                                   w // 2, h // 2, size=28, color=ui.C_GREY)
        else:
            self._render_cards(surface, w, h)

        if self._btn_back:
            self._btn_back.render(surface)

        # Superposition confirmation
        if self._confirm_idx is not None:
            self._render_confirm_overlay(surface, w, h)

    # ------------------------------------------------------------------
    # Helpers privés
    # ------------------------------------------------------------------

    def _cards_origin(self, w: int) -> tuple[int, int]:
        """Origine (x, y) de la grille de cartes."""
        cols     = min(_COLS, len(self._robots))
        grid_w   = cols * _CARD_W + (cols - 1) * _GAP
        start_x  = (w - grid_w) // 2
        start_y  = _TOP_Y - self._scroll_y
        return start_x, start_y

    def _card_rect(self, index: int, w: int) -> pygame.Rect:
        start_x, start_y = self._cards_origin(w)
        col = index % _COLS
        row = index // _COLS
        x   = start_x + col * (_CARD_W + _GAP)
        y   = start_y + row * (_CARD_H + _GAP)
        return pygame.Rect(x, y, _CARD_W, _CARD_H)

    def _delete_buttons(self) -> list[ui.Button]:
        """Génère la liste des boutons Supprimer pour chaque carte."""
        w = self.ui.screen.get_width()
        buttons = []
        for i in range(len(self._robots)):
            cr = self._card_rect(i, w)
            btn = ui.Button(
                (cr.x + _CARD_W - 90, cr.bottom - 36, 82, 28),
                "Suppr.",
                color=ui.C_DANGER, hover_color=ui.C_DANGER_HOV, font_size=16,
            )
            btn.update_hover(pygame.mouse.get_pos())
            buttons.append(btn)
        return buttons

    def _render_cards(self, surface: pygame.Surface, w: int, h: int) -> None:
        del_buttons = self._delete_buttons()
        for i, robot in enumerate(self._robots):
            cr = self._card_rect(i, w)

            # Clip : ne dessiner que si la carte est dans la zone visible
            if cr.bottom < _TOP_Y or cr.top > h - 70:
                continue

            type_color = ui.TYPE_COLORS.get(robot.type.name, ui.C_WHITE)
            pygame.draw.rect(surface, ui.C_PANEL, cr, border_radius=10)
            pygame.draw.rect(surface, type_color, cr, width=2, border_radius=10)

            # Nom
            font = ui.get_font(20, bold=True)
            name_surf = font.render(robot.name, True, ui.C_WHITE)
            surface.blit(name_surf, (cr.x + 10, cr.y + 10))

            # Type badge
            badge_font = ui.get_font(15)
            badge = badge_font.render(robot.type.value, True, type_color)
            surface.blit(badge, (cr.x + 10, cr.y + 36))

            # Stats
            stats_y = cr.y + 64
            stats = [
                (f"PV  {robot.hp}/{robot.max_hp}", ui.C_HP_BAR),
                (f"ATK {robot.attack}", (220, 80, 80)),
                (f"DEF {robot.defense}", (80, 160, 255)),
                (f"VIT {robot.speed}", (100, 220, 100)),
            ]
            for j, (txt, col) in enumerate(stats):
                sx = cr.x + 10 + (j % 2) * 120
                sy = stats_y + (j // 2) * 22
                ui.draw_text(surface, txt, sx, sy, size=16, color=col)

            # Bouton supprimer
            del_buttons[i].render(surface)

    def _render_confirm_overlay(self, surface: pygame.Surface, w: int, h: int) -> None:
        assert self._confirm_idx is not None
        robot = self._robots[self._confirm_idx]

        # Fond semi-transparent
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Boîte de dialogue
        box_w, box_h = 420, 180
        box_x = (w - box_w) // 2
        box_y = (h - box_h) // 2
        box   = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(surface, ui.C_PANEL, box, border_radius=12)
        pygame.draw.rect(surface, ui.C_DANGER, box, width=2, border_radius=12)

        ui.draw_text_centered(surface, f"Supprimer '{robot.name}' ?",
                               w // 2, box_y + 45, size=22, bold=True)
        ui.draw_text_centered(surface, "Cette action est irreversible.",
                               w // 2, box_y + 78, size=18, color=ui.C_GREY)

        # Centrer les boutons
        assert self._btn_confirm and self._btn_cancel
        self._btn_confirm.rect = pygame.Rect(w // 2 - 160, box_y + 118, 150, 44)
        self._btn_cancel.rect  = pygame.Rect(w // 2 + 10,  box_y + 118, 150, 44)
        self._btn_confirm.render(surface)
        self._btn_cancel.render(surface)

    def _delete_robot(self, index: int) -> None:
        if 0 <= index < len(self._robots):
            del self._robots[index]
            sauvegarder_robots(self._robots)
