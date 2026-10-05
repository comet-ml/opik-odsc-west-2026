# Running Opik locally

Opik self-hosts via Docker Compose. The stack includes ClickHouse for analytics, MySQL for
application state, Redis, ZooKeeper and MinIO, plus the backend and frontend services. Start
it with the `opik.sh` script in the repository root.

Once it is up, the Opik UI is served on port 5173. Point the Python SDK at your local
instance by setting `OPIK_URL_OVERRIDE=http://localhost:5173/api/`.
