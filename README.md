# SMILES Chem Transformer Agent

A molecular structure workbench and Python chemistry API using RDKit, with legacy threshold-based audit utilities maintained for compatibility. The chemistry features are deterministic cheminformatics calculations, **not** a trained molecular transformer model or experimentally validated predictions.

## What works

- **Browser workbench:** validates SMILES, generates canonical isomeric SMILES, draws 2D structures, reports atom counts and molecular weight, copies canonical strings, and exports JSON. The web interface uses RDKit WebAssembly.
- **Python chemistry:** validates SMILES and molecular valence, canonicalizes structures while retaining specified stereochemistry, calculates formula/mass/charge, reports InChI/InChIKey when available, and enumerates candidate tautomer structures.
- **Existing audit workflows:** numeric rule-based threshold evaluation, mock supervisory chat, CSV batch processing, FastAPI, and an in-memory HMAC-signed audit log.

The legacy numeric thresholds are **application rules, not IUPAC, OpenSMILES, clinical, or laboratory reference limits**. The existing workers and mock model provider do not perform chemical inference. Tautomer enumeration does not establish solution-phase abundance, pharmacological properties, or chemical stability.

## Browser application

Open `web/index.html` using a local HTTP server, or use the GitHub Pages deployment when enabled.

~~~bash
python -m http.server 8080 --directory web
~~~

Visit http://localhost:8080, enter a SMILES string and select **Analyze SMILES**. The workbench has no backend dependency. It requires an internet connection to download the pinned RDKit.js WebAssembly runtime from UNPKG; it does not send submitted SMILES to this repository's API. Browser-side computations are memory-only unless you export a JSON file.

## Python installation

CI is configured to test Python 3.10–3.12. RDKit has binary dependencies and runs as a local Python package; GitHub Pages cannot run its server-side API.

~~~bash
git clone https://github.com/abusuraihsakhri/smiles-chem-transformer-agent.git
cd smiles-chem-transformer-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[api,chem,test]"
python -m pytest -q
~~~

### Chemistry commands

~~~bash
smiles-chem-transformer-agent molecule 'CC(=O)Oc1ccccc1C(=O)O'
python -m smiles_transformer.cli molecule 'OCC' --max-tautomers 5
~~~

Output includes `canonical_smiles`, formula, weights, charge, candidate `tautomers`, and optional InChI identifiers. Unparseable or over-limit SMILES return an error rather than invented results.

### Existing audit CLI

~~~bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py chat "What is the system status?"
~~~

The legacy numerical coordinator is also exposed through the `smiles-chem-transformer-engine` entry point. These commands do not analyze SMILES unless `molecule` is used.

### REST API

~~~bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export APP_ENV=production
smiles-chem-transformer-agent serve --host 127.0.0.1 --port 8000
curl -X POST http://127.0.0.1:8000/api/molecule \
  -H 'Content-Type: application/json' \
  -d '{"smiles":"OCC","max_tautomers":10}'
~~~

The server serves the workbench at `/`, OpenAPI docs at `/docs`, and its machine-readable schema at `/openapi.json`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Runtime health metadata |
| `/api/molecule` | POST | RDKit molecular analysis |
| `/api/audit` | POST | Legacy numeric-rule audit |
| `/api/chat` | POST | Deterministic mock supervisor response |
| `/api/audit/logs` | GET | In-memory signed audit metadata and verification status |
| `/metrics` | GET | Operational counters as JSON (not Prometheus text) |

The API is **not authenticated**. Bind to localhost for local analysis. Put it behind access controls before using it with non-public information. PHI regex filtering is best-effort and **not** a HIPAA-compliance guarantee. The audit chain is kept only in memory, cannot authenticate original payload contents without retained evidence, and resets on restart. In production, `APP_ENV=production` rejects missing/known placeholder audit secrets.

### Docker

~~~bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
~~~

This exposes port 8000. For an internet-facing instance, configure authentication, TLS termination, and persistent audit storage separately.

## Development and verification

- Python tests: `python -m pytest -q`
- Syntax: `python -m compileall -q agents smiles_transformer`
- Browser JavaScript: checked by CI with `node --check`; RDKit.js is pinned to `2026.9.1` and loads through an external CDN.
- GitHub Actions: runs on Python 3.10, 3.11 and 3.12, with a separate Pages deployment workflow for static `web/`.
- Chromium/Firefox/Safari/Edge: a modern browser with WebAssembly and canvas support is required. Browser-specific compatibility has not been exhaustively certified.

## Security and data handling

No API key is embedded in the browser. The application does not expose private server files through Pages. Generated JSON exports stay on the user's device. Calls to the third-party CDN for RDKit.js may reveal network metadata to that CDN; avoid using the browser workbench where all network calls must be prohibited.

## License

MIT for this repository; RDKit and its JavaScript distribution are available under the BSD-3-Clause license. See [LICENSE](LICENSE).
