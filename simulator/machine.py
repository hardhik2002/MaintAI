from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class MachineSimulator:
    machine_id: str
    machine_type: str
    scenario: str = "healthy"
    seed: int = 42
    tick: int = 0
    tool_wear: float = 20.0

    def __post_init__(self) -> None:
        self._random = random.Random(self.seed)

    def next_reading(self) -> dict[str, str | float]:
        self.tick += 1
        cycle = math.sin(self.tick / 7)
        progress = min(1.0, self.tick / 80) if self.scenario != "healthy" else 0.0
        air = 299.5 + 1.0 * cycle + self._random.gauss(0, 0.15)
        process = air + 10.0 + self._random.gauss(0, 0.18)
        rpm = 1520 + 45 * cycle + self._random.gauss(0, 15)
        torque = 40 - 2 * cycle + self._random.gauss(0, 1.0)
        if self.scenario == "power_stress":
            rpm -= 420 * progress
            torque += 28 * progress
        elif self.scenario == "heat_stress":
            air += 2.0 * progress
            process -= 6.5 * progress
        elif self.scenario == "overstrain":
            torque += 20 * progress
            self.tool_wear += 0.8 + 1.8 * progress
        self.tool_wear = min(250, self.tool_wear + self._random.uniform(0.15, 0.45))
        return {
            "machine_id": self.machine_id,
            "type": self.machine_type,
            "air_temperature": round(air, 3),
            "process_temperature": round(process, 3),
            "rotational_speed": round(max(100, rpm), 3),
            "torque": round(max(0, torque), 3),
            "tool_wear": round(self.tool_wear, 3),
        }


def default_fleet() -> list[MachineSimulator]:
    scenarios = [
        ("MACHINE-001", "L", "healthy"),
        ("MACHINE-002", "M", "healthy"),
        ("MACHINE-003", "H", "healthy"),
        ("MACHINE-004", "L", "power_stress"),
        ("MACHINE-005", "M", "heat_stress"),
        ("MACHINE-006", "L", "overstrain"),
    ]
    return [
        MachineSimulator(machine, kind, scenario, seed=42 + index * 17)
        for index, (machine, kind, scenario) in enumerate(scenarios)
    ]
