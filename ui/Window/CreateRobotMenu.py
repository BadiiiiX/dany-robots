"""
Écran de création de robot.
Saisie du nom, sélection du type, 4 sliders PV/ATK/DEF/VIT avec total temps réel,
affichage des capacités, boutons Créer Aléatoire / Créer / Retour.
"""
from __future__ import annotations

import pygame
from ui.Window.Window import Window
from ui import ui_helpers as ui
from impl.Robot.RobotType    import RobotType
from impl.Robot.RobotFactory import RobotFactory
from impl.sauvegarde         import charger_robots, sauvegarder_robots
from impl.exceptions         import StatsInvalidesException, NomInvalideException

# Descriptions des capacités par type (affichées à l'écran)
_CAPACITES_INFO: dict[str, list[str]] = {
    RobotType.ASSAULT.name:  [
        "Tir de barrage  (30 E) : x1.5 degats",
        "Rage de combat  (40 E) : +20 ATK pdt 2 tours",
    ],
    RobotType.DEFENDER.name: [
        "Bouclier renforce  (35 E) : +15 DEF pdt 3 tours",
        "Regeneration  (50 E) : +30 PV",
    ],
    RobotType.AGILE.name:    [
        "Attaque rapide  (25 E) : 2 attaques normales",
        "Esquive  (30 E) : evite la prochaine attaque",
    ],
    RobotType.BALANCE.name:  [
        "Frappe puissante  (35 E) : x1.3 degats",
        "Recharge rapide  (20 E) : +40 energie",
    ],
}

# Plages autorisées (cohérentes avec RobotFactory)
_PV_MIN,  _PV_MAX  = RobotFactory.PV_MIN,  80   # max pratique
_ATK_MIN, _ATK_MAX = RobotFactory.ATK_MIN, RobotFactory.ATK_MAX
_DEF_MIN, _DEF_MAX = RobotFactory.DEF_MIN, RobotFactory.DEF_MAX
_SPD_MIN, _SPD_MAX = RobotFactory.SPD_MIN, RobotFactory.SPD_MAX


class CreateRobotMenu(Window):
    """Écran de création d'un robot avec interface complète."""

    def __init__(self, robot_ui):
        super().__init__(robot_ui)
        self._name_input:   ui.TextInput | None = None
        self._type_dd:      ui.Dropdown  | None = None
        self._sliders:      list[ui.Slider]     = []
        self._btn_create:   ui.Button    | None = None
        self._btn_random:   ui.Button    | None = None
        self._btn_back:     ui.Button    | None = None
        self._error_msg:    str                 = ""
        self._success_msg:  str                 = ""
        self._msg_timer:    int                 = 0

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        w, h = self.ui.screen.get_size()
        lx   = 80          # colonne gauche
        rx   = w // 2 + 40 # colonne droite
        slider_w = 340

        # --- Champ nom ---
        self._name_input = ui.TextInput(
            (lx, 120, 360, 44),
            placeholder="Nom du robot (3-20 car.)",
            max_length=20,
        )

        # --- Dropdown type ---
        self._type_dd = ui.Dropdown(
            (lx, 210, 360, 44),
            options=[t.value for t in RobotType],
            selected_index=0,
        )

        # --- Sliders ---
        slider_y   = 310
        slider_gap = 70
        initial_pv, initial_atk, initial_def, initial_spd = 60, 15, 15, 10
        self._sliders = [
            ui.Slider(lx, slider_y + 0 * slider_gap, slider_w,
                      _PV_MIN, _PV_MAX, initial_pv,
                      label="PV", color=ui.C_HP_BAR),
            ui.Slider(lx, slider_y + 1 * slider_gap, slider_w,
                      _ATK_MIN, _ATK_MAX, initial_atk,
                      label="Attaque", color=(220, 80, 80)),
            ui.Slider(lx, slider_y + 2 * slider_gap, slider_w,
                      _DEF_MIN, _DEF_MAX, initial_def,
                      label="Defense", color=(80, 160, 255)),
            ui.Slider(lx, slider_y + 3 * slider_gap, slider_w,
                      _SPD_MIN, _SPD_MAX, initial_spd,
                      label="Vitesse", color=(100, 220, 100)),
        ]

        # --- Boutons ---
        self._btn_random = ui.Button(
            (lx, 620, 160, 46), "Aleatoire",
            color=ui.C_WARNING, hover_color=(255, 210, 70), font_size=20,
        )
        self._btn_create = ui.Button(
            (lx + 175, 620, 185, 46), "Creer le robot",
            color=ui.C_SUCCESS, font_size=20,
        )
        self._btn_back = ui.Button(
            (lx, 680, 130, 40), "< Retour",
            color=ui.C_DANGER, hover_color=ui.C_DANGER_HOV, font_size=18,
        )

        self._error_msg   = ""
        self._success_msg = ""

    def on_leave(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Événements
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        assert self._name_input and self._type_dd and self._btn_back

        self._name_input.handle_event(event)
        old_type = self._type_dd.selected_index
        self._type_dd.handle_event(event)

        for slider in self._sliders:
            slider.handle_event(event)

        if self._btn_random and self._btn_random.handle_event(event):
            self._generate_random()
        if self._btn_create and self._btn_create.handle_event(event):
            self._create_robot()
        if self._btn_back.handle_event(event):
            from ui.Window.Menu import Menu
            self.ui.set_window(Menu(self.ui))

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self) -> None:
        assert self._btn_create
        total = self._total()
        self._btn_create.enabled = (total == 100)

        mouse_pos = pygame.mouse.get_pos()
        for btn in [self._btn_random, self._btn_create, self._btn_back]:
            if btn:
                btn.update_hover(mouse_pos)

        if self._msg_timer > 0:
            self._msg_timer -= 1
            if self._msg_timer == 0:
                self._error_msg   = ""
                self._success_msg = ""

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> None:
        assert self._name_input and self._type_dd
        surface = self.ui.screen
        w, h    = surface.get_size()
        lx      = 80
        rx      = w // 2 + 40
        surface.fill(ui.C_BG)

        # Titre
        ui.draw_text_centered(surface, "CREATION DE ROBOT", w // 2, 50, size=40, bold=True)

        # --- Colonne gauche ---
        ui.draw_text(surface, "Nom :", lx, 95, size=18, color=ui.C_GREY)
        self._name_input.render(surface)

        ui.draw_text(surface, "Type :", lx, 183, size=18, color=ui.C_GREY)
        # On rend le dropdown en dernier pour qu'il passe au-dessus des sliders
        for slider in self._sliders:
            slider.render(surface)

        # Total
        total = self._total()
        total_color = ui.C_SUCCESS if total == 100 else ui.C_DANGER
        ui.draw_text(surface, f"Total : {total} / 100", lx, 575, size=22, bold=True, color=total_color)

        # Boutons
        if self._btn_random:
            self._btn_random.render(surface)
        if self._btn_create:
            self._btn_create.render(surface)
        if self._btn_back:
            self._btn_back.render(surface)

        # Messages
        if self._error_msg:
            ui.draw_text(surface, self._error_msg, lx, 735, size=18, color=ui.C_DANGER)
        if self._success_msg:
            ui.draw_text(surface, self._success_msg, lx, 735, size=18, color=ui.C_SUCCESS)

        # --- Colonne droite : infos du type ---
        self._render_type_info(surface, rx, h)

        # Dropdown rendu en dernier (au-dessus de tout)
        self._type_dd.render(surface)

    def _render_type_info(self, surface: pygame.Surface, rx: int, h: int) -> None:
        assert self._type_dd
        type_name = self._selected_robot_type().name
        type_val  = self._selected_robot_type().value
        type_color = ui.TYPE_COLORS.get(type_name, ui.C_WHITE)

        # Carte type
        card = pygame.Rect(rx, 100, surface.get_width() - rx - 40, h - 140)
        pygame.draw.rect(surface, ui.C_PANEL, card, border_radius=12)
        pygame.draw.rect(surface, type_color, card, width=2, border_radius=12)

        cy = card.y + 30
        ui.draw_text_centered(surface, type_val, card.centerx, cy,
                               size=30, bold=True, color=type_color)
        cy += 50
        pygame.draw.line(surface, ui.C_BORDER,
                         (card.x + 20, cy), (card.right - 20, cy), 1)
        cy += 20

        ui.draw_text(surface, "Capacites :", card.x + 20, cy, size=20, bold=True, color=ui.C_GREY)
        cy += 32

        caps = _CAPACITES_INFO.get(type_name, [])
        for cap in caps:
            font  = ui.get_font(17)
            lines = ui.wrap_text(cap, font, card.width - 40)
            for line in lines:
                ui.draw_text(surface, line, card.x + 20, cy, size=17, color=ui.C_WHITE)
                cy += 26
            cy += 8

    # ------------------------------------------------------------------
    # Logique interne
    # ------------------------------------------------------------------

    def _total(self) -> int:
        return sum(s.value for s in self._sliders)

    def _selected_robot_type(self) -> RobotType:
        assert self._type_dd
        return list(RobotType)[self._type_dd.selected_index]

    def _generate_random(self) -> None:
        assert self._name_input
        nom = self._name_input.text.strip() or "Robot"
        try:
            robots = charger_robots()
            robot  = RobotFactory.creer_robot_aleatoire(
                nom if len(nom) >= 3 else "Robot",
                self._selected_robot_type(),
                robots_existants=robots,
            )
            # Mettre les sliders à jour avec les stats générées
            vals = [robot.hp, robot.attack, robot.defense, robot.speed]
            for slider, val in zip(self._sliders, vals):
                slider.value = val
            if len(nom) < 3:
                self._name_input.text = robot.name
        except (StatsInvalidesException, NomInvalideException) as e:
            self._show_error(str(e))

    def _create_robot(self) -> None:
        assert self._name_input
        nom = self._name_input.text.strip()
        pv  = self._sliders[0].value
        atk = self._sliders[1].value
        def_ = self._sliders[2].value
        spd = self._sliders[3].value
        try:
            robots = charger_robots()
            robot  = RobotFactory.creer_robot_manuel(
                nom,
                self._selected_robot_type(),
                pv, atk, def_, spd,
                robots_existants=robots,
            )
            robots.append(robot)
            if sauvegarder_robots(robots):
                self._show_success(f"Robot '{robot.name}' cree avec succes !")
                self._name_input.text = ""
            else:
                self._show_error("Erreur lors de la sauvegarde.")
        except NomInvalideException as e:
            self._show_error(str(e))
        except StatsInvalidesException as e:
            self._show_error(str(e))

    def _show_error(self, msg: str) -> None:
        self._error_msg   = msg[:80]
        self._success_msg = ""
        self._msg_timer   = 180  # ~6 s à 30 FPS

    def _show_success(self, msg: str) -> None:
        self._success_msg = msg
        self._error_msg   = ""
        self._msg_timer   = 180
