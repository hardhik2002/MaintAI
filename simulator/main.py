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
            responses = await asyncio.gather(
                *(client.post(f"{api_url}/api/v1/predict", json=machine.next_reading()) for machine in fleet),
                return_exceptions=True,
            )
            successful = sum(isinstance(response, httpx.Response) and response.is_success for response in responses)
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
