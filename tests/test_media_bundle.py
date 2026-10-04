from media_bundle import DeliveryBundle, build_delivery_bundle


class FakeClient:
    def __init__(self):
        self.calls = []

    def post(self, path, body):
        self.calls.append((path, body))
        if path.endswith("/merge"):
            return {"ok": True, "data": {"pdf_id": "merged-pdf"}, "error": None, "metadata": {}}
        return {"ok": True, "data": {"files": ["part-a", "part-b"]}, "error": None, "metadata": {}}


def test_creator_delivery_merges_then_splits():
    fake = FakeClient()
    result = build_delivery_bundle(["a", "b"], fake)
    assert isinstance(result, DeliveryBundle)
    assert [path for path, _ in fake.calls] == ["/v1/pdf/merge", "/v1/pdf/split"]
    assert fake.calls[0][1] == {"inputs": ["a", "b"], "store": True}
    assert fake.calls[1][1] == {"pdf": "merged-pdf", "ranges": [[1, 1], [2, 2]]}
    assert result.split["data"]["files"] == ["part-a", "part-b"]
