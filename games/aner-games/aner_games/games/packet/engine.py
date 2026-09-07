"""Packet chase rules — no TUI."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .models import HEIGHT, LIVES, WIDTH, Packet, Pos


@dataclass
class PacketGame:
    player: Pos = (2, HEIGHT // 2)
    packets: list[Packet] = field(default_factory=list)
    score: int = 0
    lives: int = LIVES
    alive: bool = True
    ticks: int = 0
    rng: random.Random = field(default_factory=random.Random)

    def move_player(self, dx: int, dy: int) -> None:
        if not self.alive:
            return
        x, y = self.player
        nx = max(0, min(WIDTH - 1, x + dx))
        ny = max(0, min(HEIGHT - 1, y + dy))
        self.player = (nx, ny)
        self._catch()

    def _catch(self) -> None:
        kept: list[Packet] = []
        px, py = self.player
        for pkt in self.packets:
            if (pkt.x, pkt.y) == (px, py):
                self.score += 10
            else:
                kept.append(pkt)
        self.packets = kept

    def _spawn(self) -> None:
        if len(self.packets) >= 8:
            return
        y = self.rng.randrange(HEIGHT)
        if self.rng.random() < 0.5:
            self.packets.append(Packet(x=0, y=y, dx=1))
        else:
            self.packets.append(Packet(x=WIDTH - 1, y=y, dx=-1))

    def tick(self) -> None:
        if not self.alive:
            return
        self.ticks += 1
        moved: list[Packet] = []
        for pkt in self.packets:
            nx = pkt.x + pkt.dx
            if nx < 0 or nx >= WIDTH:
                self.lives -= 1
                if self.lives <= 0:
                    self.alive = False
                continue
            moved.append(Packet(x=nx, y=pkt.y, dx=pkt.dx))
        self.packets = moved
        self._catch()
        if self.ticks % 4 == 1:
            self._spawn()

    def speed_s(self) -> float:
        return max(0.12, 0.22 - self.score * 0.001)
