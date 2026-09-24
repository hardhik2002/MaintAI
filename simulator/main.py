from __future__ import annotations

import argparse
import asyncio
import logging

import httpx

from simulator.machine import default_fleet

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("maintai.simulator")


async def run(api_url: str, interval: float, iterations: int | None) -> None:
    fleet = default_fleet()
    completed = 0
    async with httpx.AsyncClient(timeout=15) as client:
        while iterations is None or completed < iterations:
            successful = 0
            for machine in fleet:
                try:
                    response = await client.post(
                        f"{api_url}/api/v1/predict", json=machine.next_reading()
                    )
                    successful += int(response.is_success)
                except httpx.HTTPError as exc:
                    logger.warning("telemetry delivery failed for %s: %s", machine.machine_id, exc)
            logger.info("sent telemetry for %s/%s machines", successful, len(fleet))
            completed += 1
            await asyncio.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="MaintAI deterministic telemetry simulator")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--iterations", type=int)
    args = parser.parse_args()
    asyncio.run(run(args.api_url.rstrip("/"), args.interval, args.iterations))


if __name__ == "__main__":
    main()
