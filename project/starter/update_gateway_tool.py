"""Update the existing Lambda target's tool description without recreating it."""

import json
import time
from pathlib import Path

import boto3

from setup_gateway import TOOL_SCHEMA


def main():
    config = json.loads(Path("agentcore_config.json").read_text())
    client = boto3.client("bedrock-agentcore-control", region_name=config["region"])
    identifiers = {
        "gatewayIdentifier": config["gateway_id"],
        "targetId": config["gateway_target_id"],
    }
    target = client.get_gateway_target(**identifiers)
    configuration = target["targetConfiguration"]
    configuration["mcp"]["lambda"]["toolSchema"] = {
        "inlinePayload": [TOOL_SCHEMA]
    }
    update = {**identifiers, "targetConfiguration": configuration}
    for field in ("name", "description", "credentialProviderConfigurations",
                  "metadataConfiguration", "privateEndpoint"):
        if field in target:
            update[field] = target[field]
    client.update_gateway_target(**update)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        target = client.get_gateway_target(**identifiers)
        status = target.get("status")
        print("Target status:", status, flush=True)
        if status == "READY":
            saved = target["targetConfiguration"]["mcp"]["lambda"]["toolSchema"]
            if saved.get("inlinePayload") != [TOOL_SCHEMA]:
                raise RuntimeError("Target is READY but its schema does not match.")
            print("Updated tool schema verified on the existing target.")
            return
        if status not in ("CREATING", "UPDATING"):
            raise RuntimeError(f"Unexpected target status: {status}")
        time.sleep(5)
    raise TimeoutError("Timed out waiting for the target update.")


if __name__ == "__main__":
    main()
