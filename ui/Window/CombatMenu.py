"""
Écran de combat.
Phase 1 : sélection pré-combat (2 dropdowns, 3 modes, bouton lancer).
Phase 2 : interface de combat temps réel (barres animées, actions, journal).
Phase 3 : écran de fin avec vainqueur et bouton retour.
"""
from __future__ import annotations

import pygame
from ui.Window.Window import Window
from ui import ui_helpers as ui
from impl.sauvegarde         import charger_robots
from impl.Robot.Robot        import Robot
from impl.Combat.Combat      import (
    Combat, MODE_MANUEL, MODE_AUTO, MODE_RAPIDE,
)
from impl.Combat.ai          import (
    ACTION_ATTAQUE, ACTION_CAPACITE_1, ACTION_CAPACITE_2, ACTION_DEFENSE,
)
from impl.exceptions         import CombatImpossibleException

# ------------------------------------------------------------------
# Constantes layout
# ------------------------------------------------------------------
_ROBOT1_X  = 60           # Zone robot 1 (gauche)
_ROBOT2_X  = None         # Calculé à l'init (droite)
_ZONE_W    = 440
_ZONE_TOP  = 100
_BAR_W     = 340
_BAR_H     = 20
_JOURNAL_X = 60
_JOURNAL_Y = 540
_JOURNAL_H = 160
_AUTO_DELAY = 60          # frames entre chaque tour en mode auto
_RAPIDE_DELAY = 10        # frames entre chaque tour en mode rapide

# Phases
_PHASE_SELECT  = "select"
_PHASE_COMBAT  = "combat"
_PHASE_END     = "end"


class CombatMenu(Window):
    """Écran complet de combat (sélection → combat → fin)."""

    def __init__(self, robot_ui):
        super().__init__(robot_ui)
        self._phase: str               = _PHASE_SELECT
        self._robots: list[Robot]      = []

        # --- Phase sélection ---
        self._dd1:         ui.Dropdown | None = None
        self._dd2:         ui.Dropdown | None = None
        self._mode_btns:   list[ui.Button]    = []
        self._selected_mode: str              = MODE_MANUEL
        self._btn_launch:  ui.Button | None   = None
        self._btn_back:    ui.Button | None   = None
        self._select_error: str               = ""

        # --- Phase combat ---
        self._combat:       Combat | None     = None
        self._action_btns:  list[ui.Button]   = []
        self._journal_scroll: int             = 0
        self._auto_timer:   int               = 0
        self._combat_over:  bool              = False

        # Cibles affichées pour les barres animées
        self._hp1_disp:  float = 0.0
        self._hp2_disp:  float = 0.0
        self._en1_disp:  float = 0.0
        self._en2_disp:  float = 0.0

        # --- Phase fin ---
        self._btn_menu:    ui.Button | None   = None

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------

    def on_enter(self) -> None:
        self._robots = charger_robots()
        self._phase  = _PHASE_SELECT
        self._select_error = ""
        w, h = self.ui.screen.get_size()
        self._build_select_widgets(w, h)

    def on_leave(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Événements
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._phase == _PHASE_SELECT:
            self._handle_select(event)
        elif self._phase == _PHASE_COMBAT:
            self._handle_combat(event)
        elif self._phase == _PHASE_END:
            self._handle_end(event)

    def _handle_select(self, event: pygame.event.Event) -> None:
        assert self._dd1 and self._dd2 and self._btn_launch and self._btn_back

        self._dd1.handle_event(event)
        self._dd2.handle_event(event)

        for btn in self._mode_btns:
            if btn.handle_event(event):
                self._selected_mode = btn.label.lower().replace("auto ia", "auto")

        if self._btn_launch.handle_event(event):
            self._launch_combat()
        if self._btn_back.handle_event(event):
            from ui.Window.Menu import Menu
            self.ui.set_window(Menu(self.ui))

    def _handle_combat(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEWHEEL:
            self._journal_scroll = max(0, self._journal_scroll - event.y * 20)

        if self._combat_over:
            return

        if self._combat and self._combat.mode == MODE_MANUEL:
            for btn in self._action_btns:
                if btn.handle_event(event):
                    self._do_action(btn.label)

    def _handle_end(self, event: pygame.event.Event) -> None:
        if self._btn_menu and self._btn_menu.handle_event(event):
            from ui.Window.Menu import Menu
            self.ui.set_window(Menu(self.ui))

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()

        if self._phase == _PHASE_SELECT:
            for btn in (self._btn_launch, self._btn_back, *self._mode_btns):
                if btn:
                    btn.update_hover(mouse_pos)

        elif self._phase == _PHASE_COMBAT:
            self._update_bar_animations()
            for btn in self._action_btns:
                btn.update_hover(mouse_pos)

            # Auto / rapide : avancer le tour automatiquement
            if self._combat and not self._combat_over:
                if self._combat.mode in (MODE_AUTO, MODE_RAPIDE):
                    delay = _AUTO_DELAY if self._combat.mode == MODE_AUTO else _RAPIDE_DELAY
                    self._auto_timer += 1
                    if self._auto_timer >= delay:
                        self._auto_timer = 0
                        done = self._combat.jouer_tour()
                        self._snap_bar_targets()
                        if done:
                            self._combat_over = True
                            self._phase       = _PHASE_END
                            self._build_end_widgets()

        elif self._phase == _PHASE_END:
            if self._btn_menu:
                self._btn_menu.update_hover(mouse_pos)

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> None:
        surface = self.ui.screen
        w, h    = surface.get_size()
        surface.fill(ui.C_BG)

        if self._phase == _PHASE_SELECT:
            self._render_select(surface, w, h)
        elif self._phase == _PHASE_COMBAT:
            self._render_combat(surface, w, h)
        elif self._phase == _PHASE_END:
            self._render_end(surface, w, h)

    # ==================================================================
    # PHASE SELECTION
    # ==================================================================

    def _build_select_widgets(self, w: int, h: int) -> None:
        names = [r.name for r in self._robots]
        cx    = w // 2

        self._dd1 = ui.Dropdown((cx - 380, 160, 300, 44), names, 0)
        self._dd2 = ui.Dropdown((cx + 80,  160, 300, 44), names,
                                min(1, len(names) - 1))

        mode_labels = ["Manuel", "Auto IA", "Rapide"]
        mode_vals   = [MODE_MANUEL, MODE_AUTO, MODE_RAPIDE]
        self._mode_btns = []
        for i, (lbl, val) in enumerate(zip(mode_labels, mode_vals)):
            color = ui.C_SUCCESS if val == self._selected_mode else ui.C_ACCENT
            btn   = ui.Button(
                (cx - 210 + i * 145, 260, 130, 44),
                lbl, color=color, font_size=20,
            )
            self._mode_btns.append(btn)

        self._btn_launch = ui.Button(
            (cx - 120, 330, 240, 52), "Lancer le combat",
            color=ui.C_SUCCESS, font_size=22,
        )
        self._btn_back = ui.Button(
            (40, h - 60, 130, 40), "< Retour",
            color=ui.C_DANGER, hover_color=ui.C_DANGER_HOV, font_size=18,
        )

    def _render_select(self, surface: pygame.Surface, w: int, h: int) -> None:
        assert self._dd1 and self._dd2 and self._btn_launch and self._btn_back
        cx = w // 2

        ui.draw_text_centered(surface, "SELECTION DU COMBAT",
                               cx, 80, size=38, bold=True)
        ui.draw_text_centered(surface, "Robot 1",
                               cx - 230, 135, size=20, color=ui.C_GREY)
        ui.draw_text_centered(surface, "VS",
                               cx, 182, size=28, bold=True, color=ui.C_ACCENT)
        ui.draw_text_centered(surface, "Robot 2",
                               cx + 230, 135, size=20, color=ui.C_GREY)
        ui.draw_text_centered(surface, "Mode de jeu :",
                               cx, 240, size=20, color=ui.C_GREY)

        # Highlight du mode sélectionné
        for btn in self._mode_btns:
            mode_val = btn.label.lower().replace("auto ia", "auto")
            btn.color = ui.C_SUCCESS if mode_val == self._selected_mode else ui.C_ACCENT
            btn.render(surface)

        self._btn_launch.render(surface)
        self._btn_back.render(surface)

        if self._select_error:
            ui.draw_text_centered(surface, self._select_error,
                                   cx, 400, size=18, color=ui.C_DANGER)

        if not self._robots:
            ui.draw_text_centered(surface,
                                   "Aucun robot disponible. Creez-en depuis le menu principal.",
                                   cx, 460, size=20, color=ui.C_WARNING)
        elif len(self._robots) == 1:
            ui.draw_text_centered(surface,
                                   "Il faut au moins 2 robots pour combattre.",
                                   cx, 460, size=20, color=ui.C_WARNING)

        # Dropdowns en dernier (au-dessus)
        self._dd1.render(surface)
        self._dd2.render(surface)

    def _launch_combat(self) -> None:
        assert self._dd1 and self._dd2
        if len(self._robots) < 2:
            self._select_error = "Il faut au moins 2 robots."
            return
        r1 = self._robots[self._dd1.selected_index]
        r2 = self._robots[self._dd2.selected_index]
        if r1 is r2 or r1 == r2:
            self._select_error = "Choisissez deux robots differents."
            return
        try:
            self._combat = Combat(r1, r2, mode=self._selected_mode)
            self._combat.lancer()
        except CombatImpossibleException as e:
            self._select_error = str(e)
            return

        self._combat_over    = False
        self._auto_timer     = 0
        self._journal_scroll = 0
        self._snap_bar_targets()
        self._build_action_buttons()
        self._phase = _PHASE_COMBAT

    # ==================================================================
    # PHASE COMBAT
    # ==================================================================

    def _snap_bar_targets(self) -> None:
        """Synchronise les valeurs affichées des barres avec l'état réel."""
        if not self._combat:
            return
        r1, r2 = self._combat.robot1, self._combat.robot2
        self._hp1_disp = float(r1.hp)
        self._hp2_disp = float(r2.hp)
        self._en1_disp = float(r1.energy)
        self._en2_disp = float(r2.energy)

    def _update_bar_animations(self) -> None:
        """Anime les barres vers les valeurs cibles (interpolation linéaire)."""
        if not self._combat:
            return
        r1, r2 = self._combat.robot1, self._combat.robot2
        speed  = 4.0
        self._hp1_disp  += (r1.hp     - self._hp1_disp)  / speed
        self._hp2_disp  += (r2.hp     - self._hp2_disp)  / speed
        self._en1_disp  += (r1.energy - self._en1_disp)  / speed
        self._en2_disp  += (r2.energy - self._en2_disp)  / speed

    def _build_action_buttons(self) -> None:
        """Construit les 4 boutons d'action pour le mode manuel."""
        assert self._combat
        r1    = self._combat.robot1
        caps  = r1.capacities
        w     = self.ui.screen.get_width()
        cx    = w // 2
        btn_w = 180
        btn_h = 46
        gap   = 12
        total = 4 * btn_w + 3 * gap
        start = cx - total // 2
        y     = 478

        cap1_label = f"Cap 1 ({caps[0].energy_cost}E)" if caps else "Cap 1"
        cap2_label = f"Cap 2 ({caps[1].energy_cost}E)" if len(caps) > 1 else "Cap 2"

        self._action_btns = [
            ui.Button((start + 0 * (btn_w + gap), y, btn_w, btn_h),
                      "Attaque", color=ui.C_DANGER, font_size=18),
            ui.Button((start + 1 * (btn_w + gap), y, btn_w, btn_h),
                      cap1_label, color=ui.C_WARNING, font_size=18),
            ui.Button((start + 2 * (btn_w + gap), y, btn_w, btn_h),
                      cap2_label, color=ui.C_WARNING, font_size=18),
            ui.Button((start + 3 * (btn_w + gap), y, btn_w, btn_h),
                      "Defense", color=ui.C_ACCENT, font_size=18),
        ]

    def _update_action_buttons(self) -> None:
        """Active/désactive les boutons de capacité selon l'énergie disponible."""
        if not self._combat:
            return
        r1   = self._combat.robot1
        caps = r1.capacities
        if len(self._action_btns) >= 2 and caps:
            self._action_btns[1].enabled = (r1.energy >= caps[0].energy_cost)
        if len(self._action_btns) >= 3 and len(caps) > 1:
            self._action_btns[2].enabled = (r1.energy >= caps[1].energy_cost)

    def _do_action(self, label: str) -> None:
        """Joue un tour avec l'action choisie par le joueur."""
        if not self._combat or self._combat_over:
            return
        mapping = {
            "Attaque": ACTION_ATTAQUE,
            "Defense": ACTION_DEFENSE,
        }
        if label in mapping:
            action = mapping[label]
        elif "Cap 1" in label:
            action = ACTION_CAPACITE_1
        else:
            action = ACTION_CAPACITE_2

        done = self._combat.jouer_tour(action_robot1=action)
        self._snap_bar_targets()
        if done:
            self._combat_over = True
            self._phase       = _PHASE_END
            self._build_end_widgets()

    def _render_combat(self, surface: pygame.Surface, w: int, h: int) -> None:
        assert self._combat
        r1, r2 = self._combat.robot1, self._combat.robot2
        cx     = w // 2

        r2_x = w - _ROBOT2_X if _ROBOT2_X else w - _ZONE_W - 60

        # Titre / tour
        ui.draw_text_centered(surface,
                               f"{r1.name}  VS  {r2.name}",
                               cx, 40, size=32, bold=True)
        ui.draw_text_centered(surface,
                               f"Tour {self._combat.tour} / 50  —  Mode : {self._combat.mode}",
                               cx, 75, size=18, color=ui.C_GREY)

        # Zones robots
        self._render_robot_zone(surface, r1,  _ROBOT1_X, self._hp1_disp, self._en1_disp, flip=False)
        self._render_robot_zone(surface, r2, r2_x,        self._hp2_disp, self._en2_disp, flip=True)

        # Boutons action (mode manuel uniquement)
        if self._combat.mode == MODE_MANUEL and not self._combat_over:
            self._update_action_buttons()
            for btn in self._action_btns:
                btn.render(surface)

        # Journal
        self._render_journal(surface, w, h)

    def _render_robot_zone(
        self, surface: pygame.Surface, robot: Robot,
        x: int, hp_disp: float, en_disp: float, flip: bool,
    ) -> None:
        zone = pygame.Rect(x, _ZONE_TOP, _ZONE_W, 360)
        type_color = ui.TYPE_COLORS.get(robot.type.name, ui.C_WHITE)
        pygame.draw.rect(surface, ui.C_PANEL, zone, border_radius=12)
        pygame.draw.rect(surface, type_color, zone, width=2, border_radius=12)

        pad = 20
        cy  = zone.y + pad

        # Nom + type
        ui.draw_text(surface, robot.name, zone.x + pad, cy, size=24, bold=True)
        cy += 30
        ui.draw_text(surface, robot.type.value, zone.x + pad, cy, size=17, color=type_color)
        cy += 34

        # Barre PV
        hp_col = ui.hp_color(hp_disp, robot.max_hp)
        ui.draw_bar(surface, (zone.x + pad, cy, _BAR_W, _BAR_H),
                    hp_disp, robot.max_hp, hp_col)
        ui.draw_text(surface, f"PV: {robot.hp}/{robot.max_hp}",
                     zone.x + pad, cy + _BAR_H + 4, size=15, color=ui.C_WHITE)
        cy += _BAR_H + 24

        # Barre Energie
        ui.draw_bar(surface, (zone.x + pad, cy, _BAR_W, _BAR_H),
                    en_disp, 100, ui.C_ENERGY_BAR)
        ui.draw_text(surface, f"ENERGIE: {robot.energy}/100",
                     zone.x + pad, cy + _BAR_H + 4, size=15, color=ui.C_WHITE)
        cy += _BAR_H + 28

        # Stats ligne
        stats_txt = f"ATK: {robot.attack}   DEF: {robot.defense}   VIT: {robot.speed}"
        ui.draw_text(surface, stats_txt, zone.x + pad, cy, size=16, color=ui.C_GREY)
        cy += 28

        # Buffs actifs
        if robot.active_buffs:
            ui.draw_text(surface, "Buffs actifs:", zone.x + pad, cy, size=15, color=ui.C_WARNING)
            cy += 20
            for buff_name, buff in robot.active_buffs.items():
                txt = f"  {buff_name} ({buff.get('turns', '?')} tours)"
                ui.draw_text(surface, txt, zone.x + pad, cy, size=14, color=ui.C_WARNING)
                cy += 18

    def _render_journal(self, surface: pygame.Surface, w: int, h: int) -> None:
        assert self._combat
        journal_w = w - 2 * _JOURNAL_X
        zone      = pygame.Rect(_JOURNAL_X, _JOURNAL_Y, journal_w, _JOURNAL_H)
        pygame.draw.rect(surface, ui.C_PANEL_DARK, zone, border_radius=8)
        pygame.draw.rect(surface, ui.C_BORDER, zone, width=1, border_radius=8)

        font      = ui.get_font(15)
        line_h    = 18
        max_lines = (_JOURNAL_H - 10) // line_h
        entries   = self._combat.journal

        # Auto-scroll vers la fin
        total_lines = len(entries)
        max_scroll  = max(0, total_lines - max_lines)
        self._journal_scroll = min(self._journal_scroll, max_scroll)
        # En mode auto/rapide : défilement automatique
        if self._combat.mode in (MODE_AUTO, MODE_RAPIDE):
            self._journal_scroll = max_scroll

        visible = entries[self._journal_scroll: self._journal_scroll + max_lines]
        for i, line in enumerate(visible):
            color = ui.C_ACCENT if "***" in line else ui.C_WHITE
            surf  = font.render(line[:120], True, color)
            surface.blit(surf, (zone.x + 8, zone.y + 5 + i * line_h))

    # ==================================================================
    # PHASE FIN
    # ==================================================================

    def _build_end_widgets(self) -> None:
        w, h = self.ui.screen.get_size()
        self._btn_menu = ui.Button(
            (w // 2 - 130, h // 2 + 130, 260, 52), "Retour au menu",
            color=ui.C_ACCENT, font_size=22,
        )

    def _render_end(self, surface: pygame.Surface, w: int, h: int) -> None:
        assert self._combat
        cx = w // 2

        # Fond semi-transparent
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 500, 320
        box = pygame.Rect(cx - box_w // 2, h // 2 - box_h // 2, box_w, box_h)
        pygame.draw.rect(surface, ui.C_PANEL, box, border_radius=16)

        if self._combat.vainqueur:
            win_color = ui.TYPE_COLORS.get(self._combat.vainqueur.type.name, ui.C_WHITE)
            pygame.draw.rect(surface, win_color, box, width=3, border_radius=16)
            ui.draw_text_centered(surface, "VICTOIRE !", cx, box.y + 55,
                                   size=48, bold=True, color=win_color)
            ui.draw_text_centered(surface, self._combat.vainqueur.name,
                                   cx, box.y + 115, size=32, bold=True)
            ui.draw_text_centered(surface, "remporte le combat !",
                                   cx, box.y + 155, size=22, color=ui.C_GREY)
        else:
            pygame.draw.rect(surface, ui.C_GREY, box, width=3, border_radius=16)
            ui.draw_text_centered(surface, "MATCH NUL", cx, box.y + 80,
                                   size=48, bold=True, color=ui.C_GREY)
            ui.draw_text_centered(surface, "50 tours sans vainqueur",
                                   cx, box.y + 140, size=22, color=ui.C_GREY)

        ui.draw_text_centered(surface,
                               f"Duree : {self._combat.tour} tours",
                               cx, box.y + 200, size=18, color=ui.C_GREY)

        if self._btn_menu:
            self._btn_menu.render(surface)
