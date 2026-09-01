"""
Log Simulator - Generates fake web application log events.
Sends them to the LogMoni backend API for processing.

Usage:
    python generate_logs.py                    # Default: 10 events/sec
    python generate_logs.py --rate 50          # 50 events/sec
    python generate_logs.py --burst            # Simulate traffic burst
    python generate_logs.py --error-spike      # Simulate error spike
"""

import argparse
import asyncio
import random
import signal
import sys
from datetime import datetime, timezone

import httpx
from faker import Faker

fake = Faker()

# ============================================
# Configuration
# ============================================
API_URL = "http://localhost:8000/api/logs/batch"

PATHS = [
    "/api/users", "/api/users/{id}", "/api/products", "/api/products/{id}",
    "/api/orders", "/api/orders/{id}", "/api/cart", "/api/cart/checkout",
    "/api/auth/login", "/api/auth/register", "/api/auth/logout",
    "/api/categories", "/api/search", "/api/reviews", "/api/payments",
    "/health", "/api/notifications", "/api/settings", "/api/profile",
]

METHODS = ["GET", "GET", "GET", "GET", "POST", "PUT", "DELETE"]  # Weighted toward GET

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
    "curl/8.4.0",
    "python-httpx/0.28.1",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
]

# Status code distribution (realistic)
STATUS_WEIGHTS = {
    200: 70,  # OK
    201: 5,   # Created
    204: 3,   # No Content
    301: 2,   # Redirect
    400: 5,   # Bad Request
    401: 3,   # Unauthorized
    403: 2,   # Forbidden
    404: 6,   # Not Found
    500: 3,   # Internal Server Error
    502: 0.5, # Bad Gateway
    503: 0.5, # Service Unavailable
}

# Pre-computed weighted list for faster random selection
STATUS_CODES = []
for code, weight in STATUS_WEIGHTS.items():
    STATUS_CODES.extend([code] * int(weight * 10))


# ============================================
# Log Event Generator
# ============================================
def generate_log_event(
    error_bias: float = 0.0,
    spam_ip: str | None = None,
) -> dict:
    """Generate a single fake log event."""
    # Allow error bias for simulating spikes
    if error_bias > 0 and random.random() < error_bias:
        status_code = random.choice([500, 502, 503, 404, 400])
    else:
        status_code = random.choice(STATUS_CODES)

    # Use spam IP if provided (for simulating DDoS)
    ip_address = spam_ip if spam_ip else fake.ipv4_public()

    # Response time correlates with status
    if status_code >= 500:
        response_time = random.randint(1000, 10000)  # Slow
    elif status_code >= 400:
        response_time = random.randint(10, 200)       # Fast (rejection)
    else:
        response_time = random.randint(20, 500)        # Normal

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": random.choice(METHODS),
        "path": random.choice(PATHS).replace("{id}", str(random.randint(1, 1000))),
        "status_code": status_code,
        "ip_address": ip_address,
        "user_agent": random.choice(USER_AGENTS),
        "response_time": response_time,
    }


# ============================================
# Main Simulation Loop
# ============================================
async def run_simulator(
    rate: int = 10,
    burst: bool = False,
    error_spike: bool = False,
    batch_size: int = 10,
):
    """
    Main simulation loop.

    Args:
        rate: Events per second
        burst: Simulate periodic traffic bursts
        error_spike: Simulate error rate spikes
        batch_size: Number of events per API call
    """
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        running = False
        print("\n🛑 Stopping simulator...")

    signal.signal(signal.SIGINT, signal_handler)

    total_sent = 0
    spam_ip = fake.ipv4_public() if burst else None

    print(f"🚀 Log Simulator started!")
    print(f"   Rate: {rate} events/sec")
    print(f"   Burst mode: {'ON' if burst else 'OFF'}")
    print(f"   Error spike: {'ON' if error_spike else 'OFF'}")
    print(f"   Target: {API_URL}")
    print(f"   Press Ctrl+C to stop\n")

    async with httpx.AsyncClient(timeout=10.0) as client:
        while running:
            try:
                # Determine current rate (simulate bursts)
                current_rate = rate
                error_bias = 0.0

                if burst and random.random() < 0.1:  # 10% chance of burst
                    current_rate = rate * 5
                    print(f"💥 Traffic burst! Rate: {current_rate}/sec")

                if error_spike and random.random() < 0.05:  # 5% chance of error spike
                    error_bias = 0.8
                    print(f"🔴 Error spike! 80% error rate")

                # Generate batch
                events = [
                    generate_log_event(
                        error_bias=error_bias,
                        spam_ip=spam_ip if (burst and random.random() < 0.3) else None,
                    )
                    for _ in range(min(batch_size, current_rate))
                ]

                # Send batch to API
                response = await client.post(
                    API_URL,
                    json={"events": events},
                )

                total_sent += len(events)

                if response.status_code == 202:
                    print(f"✅ Sent {len(events)} events (total: {total_sent})", end="\r")
                else:
                    print(f"⚠️ API returned {response.status_code}: {response.text[:100]}")

                # Wait based on rate
                await asyncio.sleep(batch_size / current_rate)

            except httpx.ConnectError:
                print("❌ Cannot connect to API. Is the backend running?")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(1)

    print(f"\n📊 Total events sent: {total_sent}")


# ============================================
# CLI Entry Point
# ============================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LogMoni Log Simulator")
    parser.add_argument("--rate", type=int, default=10, help="Events per second (default: 10)")
    parser.add_argument("--burst", action="store_true", help="Enable periodic traffic bursts")
    parser.add_argument("--error-spike", action="store_true", help="Enable periodic error spikes")
    parser.add_argument("--batch-size", type=int, default=10, help="Events per batch (default: 10)")

    args = parser.parse_args()

    asyncio.run(run_simulator(
        rate=args.rate,
        burst=args.burst,
        error_spike=args.error_spike,
        batch_size=args.batch_size,
    ))
