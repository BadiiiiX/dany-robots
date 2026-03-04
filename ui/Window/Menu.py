"""
Écran principal du jeu.
Affiche le titre et les 4 boutons de navigation.
"""
import pygame
from ui.Window.Window import Window
from ui import ui_helpers as ui


class Menu(Window):
    """Menu principal avec titre et 4 boutons de navigation."""

    def __init__(self, robot_ui):
        super().__init__(robot_ui)
        self._buttons: list[ui.Button] = []

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        w, h = self.ui.screen.get_size()
        cx   = w // 2

        btn_w, btn_h = 320, 56
        gap          = 18
        start_y      = h // 2 - 60

        labels = [
            "Creer un robot",
            "Mes robots",
            "Combat",
            "Quitter",
        ]
        colors = [ui.C_ACCENT, ui.C_ACCENT, ui.C_SUCCESS, ui.C_DANGER]
        hover  = [ui.C_ACCENT_HOV, ui.C_ACCENT_HOV, (90, 230, 130), ui.C_DANGER_HOV]

        self._buttons = []
        for i, (label, color, hov) in enumerate(zip(labels, colors, hover)):
            rect = (cx - btn_w // 2, start_y + i * (btn_h + gap), btn_w, btn_h)
            self._buttons.append(
                ui.Button(rect, label, color=color, hover_color=hov, font_size=24)
            )

    def on_leave(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Événements
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self._buttons:
            if btn.handle_event(event):
                self._on_click(btn.label)

    def _on_click(self, label: str) -> None:
        # Import local pour éviter les imports circulaires
        from ui.Window.CreateRobotMenu import CreateRobotMenu
        from ui.Window.RobotListMenu   import RobotListMenu
        from ui.Window.CombatMenu      import CombatMenu

        if label == "Creer un robot":
            self.ui.set_window(CreateRobotMenu(self.ui))
        elif label == "Mes robots":
            self.ui.set_window(RobotListMenu(self.ui))
        elif label == "Combat":
            self.ui.set_window(CombatMenu(self.ui))
        elif label == "Quitter":
            self.ui.running = False

    # ------------------------------------------------------------------
    # Update / Render
    # ------------------------------------------------------------------

    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for btn in self._buttons:
            btn.update_hover(mouse_pos)

    def render(self) -> None:
        surface = self.ui.screen
        w, h    = surface.get_size()

        surface.fill(ui.C_BG)

        # Titre
        ui.draw_text_centered(surface, "ROBOT ARENA", w // 2, h // 2 - 210,
                               size=72, bold=True, color=ui.C_ACCENT)
        ui.draw_text_centered(surface, "Combat de robots futuristes", w // 2, h // 2 - 145,
                               size=24, color=ui.C_GREY)

        # Séparateur
        pygame.draw.line(surface, ui.C_BORDER,
                         (w // 2 - 200, h // 2 - 120),
                         (w // 2 + 200, h // 2 - 120), 1)

        for btn in self._buttons:
            btn.render(surface)
