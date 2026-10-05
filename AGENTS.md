# AGENTS.md

Experiment repo for automatic OpenCV "settings" detection (for the Outline document-scanner app).
Two **independent** components with no shared build tooling and no root-level build/test command — `cd` into the component you're working on.

- `image-repo/` — Kotlin **Ktor** server (Gradle wrapper): image upload to S3 + user CRUD.
- `ml/` — Python **TensorFlow/Keras** scripts: predict 22 normalized pipeline parameters from a 128×128 image.

No CI, no root formatter/linter, no root `.gitignore`. There is no monorepo tooling tying these together.

## image-repo (Ktor / Gradle)

Run all Gradle commands from `image-repo/` (uses the committed wrapper: Gradle 8.14.3, Kotlin 2.1.10, Ktor 3.2.2).

- `./gradlew run` — dev server on port 8080
- `./gradlew test` — run all tests
- `./gradlew test --tests "lv.georgs.image.ApplicationTest"` — single test class (or `--tests "*UploadTest*"`)
- `./gradlew build` / `./gradlew buildFatJar` — build / fat JAR

Entrypoint: `src/main/kotlin/lv/georgs/image/Application.kt`. `mainClass` is `io.ktor.server.netty.EngineMain` (config-driven), and `Application.module()` wires features in order: Security → Monitoring → Serialization → Databases → Administration → Routing → ImageUpload. Each `configureX()` lives in its own file in that package.

Gotchas:
- **Package is `lv.georgs.image`** (note the `.image`), even though the Gradle `group` is `lv.georgs`.
- **`application.yaml` module string is stale**: it says `lv.georgs.ApplicationKt.module`, but the real class is `lv.georgs.image.ApplicationKt`. `./gradlew run` will fail to load the module until this is corrected to `lv.georgs.image.ApplicationKt.module`.
- **Upload needs S3/MinIO.** `POST /upload-image` writes to bucket `outline-images` via the AWS SDK S3 client (`upload/S3Bucket.kt`), endpoint from `s3.url` (defaults to `localhost:9000`). Start MinIO with `docker/start_s3.sh`, then create the `outline-images` bucket via the console at http://127.0.0.1:9001. Env vars `S3_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY` (default `minioadmin`/`minioadmin`).
- **`UploadTest` hits real S3** and returns 500 (fails) unless MinIO is running with the bucket. `ApplicationTest` (GET `/`) passes without S3.
- DB is **in-memory H2** (`jdbc:h2:mem:test`) — user CRUD at `/users` is not persistent across restarts.

## ml (TensorFlow)

Run scripts **from `ml/`** — they use relative paths (`data/`, `settings_predictor_model.keras`).

- venv lives at `ml/venv` (has `tensorflow` 2.19). Install deps: `pip install -r requirements.txt` (tensorflow, numpy, opencv-python).
- `python scripts/train.py` — trains from `data/<sample>/` dirs and saves `settings_predictor_model.keras` in the cwd.
- `python scripts/test.py` — loads that model and predicts on `data/multi_tools.jpg`.

Data format: each `data/<sample>/` holds an image (`image.jpg|jpeg|png`) plus `settings.json` whose top-level `settings` object is the Outline scan settings. `encode_settings` (train.py) and `decode_settings` (test.py) define the same 22-value normalized vector in the **same order** — edit both together or predictions desync.

`ml/.gitignore` ignores `data/`, `models/`, and `*.keras`, so the sample data and the trained model are local-only and not committed.
