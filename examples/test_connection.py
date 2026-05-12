"""Quick connection check for AbletonOSC."""

from ableton_bridge.config import AbletonBridgeConfig
from ableton_bridge.errors import AbletonOSCError
from ableton_bridge.osc_client import AbletonOSCClient


def main() -> int:
    client = AbletonOSCClient(AbletonBridgeConfig())
    try:
        print(f"AbletonOSC status: {client.status()}")
    except AbletonOSCError as exc:
        print(f"Could not reach AbletonOSC: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
