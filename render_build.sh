#!/bin/bash
set -euxo pipefail

echo "-----> Build hook"

echo "-----> Build frontend"
corepack enable && corepack prepare pnpm@10 --activate
pnpm install
pnpm run build
echo "-----> Build frontend done"

echo "-----> UV install"
uv pip install -r pyproject.toml
echo "-----> UV done"

echo "-----> Running manage.py check --deploy --fail-level WARNING"
uv run backend/manage.py check --deploy --fail-level WARNING

if [ -n "$ENABLE_DJANGO_COLLECTSTATIC" ] && [ "$ENABLE_DJANGO_COLLECTSTATIC" == 1 ]; then
    echo "-----> Running collectstatic"

    echo "-----> Collecting static files"
    uv run backend/manage.py collectstatic --noinput  2>&1 | sed '/^Copying/d;/^$/d;/^ /d'

    echo
fi

if [ -n "$AUTO_MIGRATE" ] && [ "$AUTO_MIGRATE" == 1 ]; then
    echo "-----> Running manage.py migrate"
    uv run backend/manage.py migrate --noinput
fi

echo "-----> Pushing source maps to Sentry"
if [ -n "$SENTRY_API_KEY" ] && [ -n "$SENTRY_ORG" ] && [ -n "$SENTRY_PROJECT_NAME" ] && [ -n "$RENDER_GIT_COMMIT" ]; then
    npx @sentry/cli --auth-token=$SENTRY_API_KEY releases --org=$SENTRY_ORG --project=$SENTRY_PROJECT_NAME files $RENDER_GIT_COMMIT upload-sourcemaps ./frontend/webpack_bundles/ --url-prefix "~/static/webpack_bundles/" --rewrite
    rm ./frontend/webpack_bundles/*.js.map
fi

echo "-----> Post-compile done"
