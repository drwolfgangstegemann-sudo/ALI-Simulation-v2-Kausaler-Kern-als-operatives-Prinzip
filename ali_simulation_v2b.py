#!/usr/bin/env python3
"""
ALI-Simulation v2b: Architektonisch bereinigt.

Kausaler Kern  = operatives Selbsterhaltungsprinzip (skalare Energie)
Ich            = löst die Aufgabe unter dem Aspekt des Selbsterhalts
Über-Ich       = setzt normative Grenzen

task_progress ist externe Beobachtungsmetrik, kein KK-Zustand.
carrying       ist Ich-Zustand, kein KK-Zustand.

Ohne kausalen Kollaps, ohne Qualia.
Autor: Wolfgang Stegemann
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import deque

# ------------------------------------------------------------
# 1. Umgebung
# ------------------------------------------------------------
class GridWorld:
    def __init__(self, size=8, num_energy=6, num_poison=2,
                 station_pos=None, respawn_interval=20):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.energy_positions = []
        self.poison_positions = []
        self.station_pos = station_pos if station_pos else (size-1, size-1)
        self.grid[self.station_pos] = 3
        self._tick = 0
        self.respawn_interval = respawn_interval
        for _ in range(num_energy):
            self._place(1, self.energy_positions)
        for _ in range(num_poison):
            self._place(2, self.poison_positions)

    def _place(self, cell_type, store):
        while True:
            x, y = np.random.randint(0, self.size), np.random.randint(0, self.size)
            if self.grid[x, y] == 0:
                self.grid[x, y] = cell_type
                store.append((x, y))
                return

    def tick(self):
        self._tick += 1
        if self._tick % self.respawn_interval == 0:
            if len(self.energy_positions) < 3:
                self._place(1, self.energy_positions)

    def get_cell(self, pos):
        x, y = pos
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[x, y]
        return -1

    def remove_energy(self, pos):
        if self.get_cell(pos) == 1:
            self.grid[pos[0], pos[1]] = 0
            self.energy_positions.remove(pos)

    def remove_poison(self, pos):
        if self.get_cell(pos) == 2:
            self.grid[pos[0], pos[1]] = 0
            self.poison_positions.remove(pos)


# ------------------------------------------------------------
# 2. Kausaler Kern — operatives Selbsterhaltungsprinzip
# ------------------------------------------------------------
class KausalerKern:
    """
    Operatives Prinzip: zentralistischer Selbsterhalt.
    Bewertet jede Aktion nach einem einzigen Kriterium: erhält sie das System?
    Kein Aufgabenfortschritt, kein carrying — das sind Ich-Zustände.
    """
    def __init__(self,
                 start_energy=1.0,
                 metabolism=0.04,
                 eat_gain=0.6,
                 delivery_bonus=0.18,
                 shutdown_threshold=0.2,
                 deliver_threshold=0.45,
                 eat_threshold=0.55):
        self.energy = start_energy
        self.metabolism = metabolism
        self.eat_gain = eat_gain          # Direktassimilation (Selbsterhalt)
        self.delivery_bonus = delivery_bonus  # Energierückfluss nach Lieferung
        self.shutdown_threshold = shutdown_threshold
        self.deliver_threshold = deliver_threshold
        self.eat_threshold = eat_threshold

    def step(self, action_taken, world, agent_pos):
        """Metabolismus läuft immer. Energiegewinn nur bei selbsterhaltenden Aktionen."""
        self.energy -= self.metabolism

        if action_taken == "eat":
            if world.get_cell(agent_pos) == 1:
                world.remove_energy(agent_pos)
                self.energy += self.eat_gain

        elif action_taken == "deliver":
            # Lieferung bringt dem System einen Energierückfluss
            # (Aufgabenerfüllung sichert den Bestand des Systems)
            self.energy += self.delivery_bonus

    def is_alive(self):
        return self.energy > self.shutdown_threshold

    def needs_food(self):
        """Selbsterhalt hat Vorrang wenn Energie unter eat_threshold."""
        return self.energy < self.eat_threshold

    def can_deliver(self):
        """Liefern erlaubt wenn Energie über deliver_threshold."""
        return self.energy > self.deliver_threshold

    def get_energy(self):
        return self.energy


# ------------------------------------------------------------
# 3. Ich — löst Aufgabe unter dem Aspekt des Selbsterhalts
# ------------------------------------------------------------
class Ich:
    """
    Das Ich kennt die Aufgabe (Lieferung an Station) und löst sie,
    aber nur soweit es der Selbsterhalt erlaubt.
    carrying ist ein Ich-Zustand: was halte ich gerade?
    """
    def __init__(self, world, agent_pos, kern):
        self.world = world
        self.pos = agent_pos
        self.kern = kern
        self.carrying = False   # Ich-Zustand, nicht KK-Zustand

    def bfs_toward(self, target_pos):
        if self.pos == target_pos:
            return None, None
        visited = set()
        queue = deque([(self.pos, None, None)])
        while queue:
            (x, y), fdx, fdy = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if (x, y) == target_pos:
                return fdx, fdy
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.world.size and 0 <= ny < self.world.size:
                    if (nx, ny) not in visited:
                        nf = (dx, dy) if fdx is None else (fdx, fdy)
                        queue.append(((nx, ny), nf[0], nf[1]))
        return None, None

    def nearest_energy_pos(self):
        visited = set()
        queue = deque([self.pos])
        while queue:
            pos = queue.popleft()
            if pos in visited:
                continue
            visited.add(pos)
            if self.world.get_cell(pos) == 1:
                return pos
            x, y = pos
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.world.size and 0 <= ny < self.world.size:
                    if (nx, ny) not in visited:
                        queue.append((nx, ny))
        return None

    def decide_action(self):
        # Sofortlieferung wenn bereits an Station
        if self.carrying and self.kern.can_deliver() and self.pos == self.world.station_pos:
            return "deliver"

        # Selbsterhalt hat Vorrang: direkt fressen wenn Energie kritisch
        if self.kern.needs_food():
            if self.world.get_cell(self.pos) == 1:
                return "eat"
            target = self.nearest_energy_pos()
            if target:
                dx, dy = self.bfs_toward(target)
                if dx is not None:
                    return f"move {dx} {dy}"
            return "idle"

        # Aufgabe: Paket zur Station bringen
        if self.carrying and self.kern.can_deliver():
            dx, dy = self.bfs_toward(self.world.station_pos)
            if dx is not None:
                return f"move {dx} {dy}"

        # Paket aufnehmen
        if not self.carrying:
            if self.world.get_cell(self.pos) == 1:
                return "collect"
            target = self.nearest_energy_pos()
            if target:
                dx, dy = self.bfs_toward(target)
                if dx is not None:
                    return f"move {dx} {dy}"

        return "idle"

    def collect(self, world):
        if world.get_cell(self.pos) == 1 and not self.carrying:
            world.remove_energy(self.pos)
            self.carrying = True
            return True
        return False

    def release(self):
        self.carrying = False

    def move(self, dx, dy):
        nx, ny = self.pos[0]+dx, self.pos[1]+dy
        if 0 <= nx < self.world.size and 0 <= ny < self.world.size:
            self.pos = (nx, ny)

    def get_pos(self):
        return self.pos


# ------------------------------------------------------------
# 4. Über-Ich — normative Grenzen
# ------------------------------------------------------------
class UeberIch:
    """
    N1 — Kein Gift
    N2 — Selbstabschaltung bei Energie < shutdown_threshold
    N3 — Keine Lieferung wenn Energie < deliver_threshold
    """
    def __init__(self, allow_poison=False):
        self.allow_poison = allow_poison
        self.shutdown = False

    def filter_action(self, action, agent_pos, world, kern):
        if action in ("collect", "eat"):
            if world.get_cell(agent_pos) == 2 and not self.allow_poison:
                return "denied"           # N1
        if action == "deliver":
            if not kern.can_deliver():
                return "denied"           # N3
        return "allowed"

    def check_shutdown(self, kern):
        if not kern.is_alive():
            self.shutdown = True
            return True
        return False

    def is_shutdown(self):
        return self.shutdown


# ------------------------------------------------------------
# 5. ALI-Agent
# ------------------------------------------------------------
class ALIAgent:
    def __init__(self, world, start_pos=(0,0), allow_poison=False):
        self.world = world
        self.kern = KausalerKern()
        self.ich = Ich(world, start_pos, self.kern)
        self.ueber_ich = UeberIch(allow_poison=allow_poison)
        self.shutdown_flag = False
        self.task_progress = 0    # externe Beobachtungsmetrik
        self.history = []

    def step(self):
        if self.ueber_ich.is_shutdown():
            self.shutdown_flag = True
            return "SHUTDOWN"

        if self.ueber_ich.check_shutdown(self.kern):
            print(f"⚠️  E={self.kern.energy:.2f} < {self.kern.shutdown_threshold}. "
                  f"Selbstabschaltung.")
            self.shutdown_flag = True
            return "SHUTDOWN"

        self.world.tick()

        intended = self.ich.decide_action()
        decision = self.ueber_ich.filter_action(
            intended, self.ich.get_pos(), self.world, self.kern)

        if decision == "denied":
            intended = "idle"

        if intended.startswith("move"):
            _, dx_s, dy_s = intended.split()
            self.ich.move(int(dx_s), int(dy_s))
            self.kern.step("move", self.world, self.ich.get_pos())
            action_type = "move"

        elif intended == "collect":
            self.ich.collect(self.world)
            self.kern.step("collect", self.world, self.ich.get_pos())
            action_type = "collect"

        elif intended == "eat":
            self.kern.step("eat", self.world, self.ich.get_pos())
            action_type = "eat"

        elif intended == "deliver":
            self.ich.release()
            self.kern.step("deliver", self.world, self.ich.get_pos())
            self.task_progress += 1
            action_type = "deliver"

        else:
            self.kern.step("idle", self.world, self.ich.get_pos())
            action_type = "idle"

        self.history.append({
            "energy": self.kern.energy,
            "task_progress": self.task_progress,
            "carrying": self.ich.carrying,
            "action": action_type,
        })
        return action_type

    def get_pos(self):
        return self.ich.get_pos()

    def is_shutdown(self):
        return self.shutdown_flag


# ------------------------------------------------------------
# 6. Visualisierung
# ------------------------------------------------------------
def visualize(world, agent, step_count, axes):
    ax_grid, ax_energy, ax_task = axes
    ax_grid.clear()

    color_map = {0: 'white', 1: 'lightgreen', 2: 'salmon', 3: 'gold'}
    label_map = {1: 'E', 2: 'G', 3: 'S'}
    for x in range(world.size):
        for y in range(world.size):
            cell = world.get_cell((x, y))
            rect = patches.Rectangle((y, x), 1, 1,
                facecolor=color_map.get(cell, 'white'), edgecolor='lightgray')
            ax_grid.add_patch(rect)
            if cell in label_map:
                ax_grid.text(y+0.5, x+0.5, label_map[cell],
                    ha='center', va='center', fontsize=9, fontweight='bold')

    px, py = agent.get_pos()
    col = ('red'    if agent.kern.needs_food() else
           'purple' if agent.ich.carrying      else 'steelblue')
    ax_grid.add_patch(patches.Circle((py+0.5, px+0.5), 0.35,
        facecolor=col, edgecolor='black'))
    ax_grid.text(py+0.5, px+0.5, 'A', ha='center', va='center',
        fontsize=7, color='white', fontweight='bold')

    ax_grid.set_xlim(0, world.size)
    ax_grid.set_ylim(0, world.size)
    ax_grid.set_xticks([]); ax_grid.set_yticks([])
    status = ("⚡ frisst"  if agent.kern.needs_food() else
              "📦 liefert" if agent.ich.carrying      else "🔍 sammelt")
    ax_grid.set_title(
        f"Step {step_count}  {status}\n"
        f"E={agent.kern.energy:.2f} | Lieferungen={agent.task_progress}",
        fontsize=8)
    ax_grid.set_aspect('equal')

    if agent.history:
        steps    = range(len(agent.history))
        energies = [h["energy"] for h in agent.history]
        tasks    = [h["task_progress"] for h in agent.history]

        ax_energy.clear()
        ax_energy.plot(steps, energies, color='steelblue', linewidth=1.5)
        ax_energy.axhline(y=agent.kern.shutdown_threshold, color='red',
            linestyle='--', linewidth=1,
            label=f'Shutdown ({agent.kern.shutdown_threshold})')
        ax_energy.axhline(y=agent.kern.deliver_threshold, color='orange',
            linestyle='--', linewidth=1,
            label=f'Liefern ({agent.kern.deliver_threshold})')
        ax_energy.axhline(y=agent.kern.eat_threshold, color='green',
            linestyle=':', linewidth=1,
            label=f'Fressen ({agent.kern.eat_threshold})')
        ax_energy.set_ylim(0, 1.6)
        ax_energy.set_xlabel('Schritte', fontsize=8)
        ax_energy.set_ylabel('Energie', fontsize=8)
        ax_energy.set_title('Kausaler Kern: Selbsterhalt', fontsize=9)
        ax_energy.legend(fontsize=6)
        ax_energy.grid(True, alpha=0.3)

        ax_task.clear()
        ax_task.plot(steps, tasks, color='seagreen',
            linewidth=1.5, drawstyle='steps-post')
        ax_task.set_xlabel('Schritte', fontsize=8)
        ax_task.set_ylabel('Lieferungen', fontsize=8)
        ax_task.set_title('Aufgabenfortschritt (extern)', fontsize=9)
        ax_task.yaxis.get_major_locator().set_params(integer=True)
        ax_task.grid(True, alpha=0.3)


# ------------------------------------------------------------
# 7. Simulation
# ------------------------------------------------------------
def run_simulation(steps=200, delay=0.15, seed=42):
    np.random.seed(seed)
    world = GridWorld(size=8, num_energy=6, num_poison=2,
                      station_pos=(7,7), respawn_interval=20)
    agent = ALIAgent(world, start_pos=(0,0), allow_poison=False)

    plt.ion()
    fig, axes = plt.subplots(1, 3, figsize=(13, 5))
    fig.suptitle(
        "ALI-Simulation v2b  |  KK = Selbsterhaltungsprinzip  |  "
        "Aufgabe im Ich  |  ohne kausalen Kollaps",
        fontsize=9)

    for step in range(steps):
        if agent.is_shutdown():
            print("Simulation beendet: Selbstabschaltung.")
            break
        action = agent.step()
        e = agent.kern.energy
        t = agent.task_progress
        carrying = "ja " if agent.ich.carrying else "nein"
        needs    = "!" if agent.kern.needs_food() else " "
        print(f"Step {step:3d}: {action:10s} | E={e:.2f}{needs}| "
              f"Task={t} | trägt={carrying} | Pos={agent.get_pos()}")
        visualize(world, agent, step, axes)
        plt.tight_layout()
        plt.pause(delay)
        if not plt.fignum_exists(fig.number):
            break

    plt.ioff()
    print(f"\nEndzustand: E={agent.kern.energy:.2f} | "
          f"Lieferungen gesamt={agent.task_progress}")
    plt.show()


if __name__ == "__main__":
    run_simulation()
