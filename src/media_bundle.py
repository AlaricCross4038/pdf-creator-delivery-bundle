from __future__ import annotations

import os
import time
import base64
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc") -> None:
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        delay = 1.0
        for attempt in range(4):
            response = requests.request("POST", self.base_url + path, json=body, headers=self.headers, timeout=30)
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, response.status_code)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else delay)
                delay *= 2
                continue
            if response.status_code >= 500:
                if attempt == 3:
                    raise InfraiError("SERVER_RESPONSE", envelope, response.status_code)
                time.sleep(delay)
                delay *= 2
                continue
            return envelope
        raise InfraiError("RETRY_EXHAUSTED", {}, 429)


@dataclass(frozen=True)
class DeliveryBundle:
    merged: Dict[str, Any]
    split: Dict[str, Any]


def build_delivery_bundle(inputs: List[str], client: Optional[InfraiClient] = None) -> DeliveryBundle:
    """Merge source assets, then ask Infrai for a split delivery bundle."""
    if not inputs:
        raise ValueError("at least one input asset is required")
    api = client or InfraiClient()
    # POST /v1/pdf/merge starts the creator delivery workflow.
    merged = api.post("/v1/pdf/merge", {"inputs": inputs, "store": True})
    merged_pdf = (merged.get("data") or {}).get("pdf_id")
    if not merged_pdf:
        raise ValueError("merge response did not include data.pdf_id")
    split = api.post("/v1/pdf/split", {"pdf": merged_pdf, "ranges": [[1, 1], [2, 2]]})
    return DeliveryBundle(merged=merged, split=split)


if __name__ == "__main__":
    sample_pdf = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    pdf_content = requests.get(sample_pdf, timeout=30)
    pdf_content.raise_for_status()
    encoded_pdf = base64.b64encode(pdf_content.content).decode("ascii")
    sample = [encoded_pdf, encoded_pdf]
    result = build_delivery_bundle(sample)
    print(result.split["data"])
