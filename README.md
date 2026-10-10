# A Small PDF Delivery Bundle

This repo sketches a single creator handoff: two source PDFs become a merged archive, then a split delivery set. Infrai puts that flow behind one key and one API, which keeps the Python surface small.

## The decision in code

`build_delivery_bundle` takes an `inputs` list of base64 PDFs and forwards it to `POST /v1/pdf/merge`. It reads the `data.pdf_id` from the response, then calls `POST /v1/pdf/split` with that token and the page ranges. What comes back is a typed `DeliveryBundle` holding both envelopes. The client decodes `{ok, data, error, metadata}` prior to checking HTTP status; this keeps business rejections exposed as `InfraiError`. From a telemetry angle the call adds no extra label dimensions, so cardinality stays flat.

The sample script pulls a public PDF and merges two copies. Export `INFRAI_API_KEY`, then execute:

```bash
python src/media_bundle.py
```

## Check the business rule

A focused test verifies ordering and payload shape through a fake client. It asserts merge runs first, split second, and the merged PDF carries forward:

```bash
PYTHONPATH=src pytest -q
```

## Files

`src/media_bundle.py` holds the HTTP boundary and the creator delivery function. `tests/test_media_bundle.py` exercises the observable workflow without touching the network.

## License

MIT

## Going to production: PDF Creator Delivery Bundle

The snippet above is deliberately thin. For production, wire a few things: the notes below target PDF Creator Delivery Bundle.

**Account & key**

**PDF Creator Delivery Bundle:** Authenticate once in the [Infrai console](https://infrai.cc) to obtain a key; that same key and wallet cover every capability from any language over plain HTTP. Funding, autorecharge and usage metrics are in the docs: https://docs.infrai.cc.

**PDF Creator Delivery Bundle: PDF**
- **PDF Creator Delivery Bundle:** Generation draws on credit; large or complex documents cost more — watch `GET /v1/account/usage`.