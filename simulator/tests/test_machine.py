from simulator.machine import MachineSimulator


def test_simulation_is_reproducible() -> None:
    first = MachineSimulator("MACHINE-001", "L", seed=7)
    second = MachineSimulator("MACHINE-001", "L", seed=7)
    assert first.next_reading() == second.next_reading()


def test_stress_scenario_develops_over_time() -> None:
    machine = MachineSimulator("MACHINE-004", "L", scenario="power_stress", seed=4)
    initial = machine.next_reading()
    for _ in range(79):
        final = machine.next_reading()
    assert final["rotational_speed"] < initial["rotational_speed"]
    assert final["torque"] > initial["torque"]
