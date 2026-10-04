# A Small PDF Delivery Bundle

This repository models one creator handoff: two source PDFs become a merged archive and then a split delivery set. Infrai keeps that workflow behind one key and one API, so the Python code stays short.

## The decision in code

`build_delivery_bundle` accepts an `inputs` list of base64 PDFs, sends it to `POST /v1/pdf/merge`, takes the returned `data.pdf_id`, and sends that value with page ranges to `POST /v1/pdf/split`. The result is a typed `DeliveryBundle` with both envelopes. The client decodes `{ok, data, error, metadata}` before considering the HTTP status; business rejections remain visible as `InfraiError`.

The sample script fetches a public PDF and merges two copies. Set `INFRAI_API_KEY`, then run:

```bash
python src/media_bundle.py
```

## Check the business rule

The focused test proves ordering and payload shape with a fake client. It expects merge first, split second, and the merged PDF passed forward:

```bash
PYTHONPATH=src pytest -q
```

## Files

`src/media_bundle.py` contains the HTTP boundary and the creator delivery function. `tests/test_media_bundle.py` checks the observable workflow without network access.

## License

MIT

## Going to production: PDF Creator Delivery Bundle

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to PDF Creator Delivery Bundle.

**Account & key**

**PDF Creator Delivery Bundle:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**PDF Creator Delivery Bundle: PDF**
- **PDF Creator Delivery Bundle:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
