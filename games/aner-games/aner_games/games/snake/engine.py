"""Pure snake rules — no TUI."""

from __future__ import annotations

from dataclasses import dataclass

from .models import OPPOSITE, SnakeState


@dataclass
class SnakeGame(SnakeState):
    def __post_init__(self) -> None:
        if not self.body:
            cx, cy = self.width // 3, self.height // 2
            self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.food = self._place_food()
        if self.food is None:
            self.won = True
            self.alive = False

    def set_direction(self, dx: int, dy: int) -> None:
        if not self.alive:
            return
        nxt = (dx, dy)
        current = self.pending or self.direction
        if nxt == OPPOSITE.get(current):
            return
        if nxt not in OPPOSITE:
            return
        self.pending = nxt

    def tick(self) -> None:
        if not self.alive:
            return
        if self.pending:
            self.direction = self.pending
            self.pending = None
        hx, hy = self.body[0]
        dx, dy = self.direction
        nx, ny = hx + dx, hy + dy
        if nx < 0 or ny < 0 or nx >= self.width or ny >= self.height:
            self.alive = False
            return
        grow = self.food is not None and (nx, ny) == self.food
        body_hit = set(self.body if grow else self.body[:-1])
        if (nx, ny) in body_hit:
            self.alive = False
            return
        self.body.insert(0, (nx, ny))
        if grow:
            self.score += 1
            self.food = self._place_food()
            if self.food is None:
                self.won = True
                self.alive = False
        else:
            self.body.pop()

    def _place_food(self) -> tuple[int, int] | None:
        occupied = set(self.body)
        empty = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in occupied
        ]
        if not empty:
            return None
        return self.rng.choice(empty)

    def speed_s(self) -> float:
        return max(0.06, 0.14 - self.score * 0.004)
