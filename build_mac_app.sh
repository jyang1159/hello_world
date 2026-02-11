#!/usr/bin/env bash
set -euo pipefail

APP_NAME="24 Points Game"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
DIST_DIR="${PROJECT_DIR}/dist-universal"
WORK_DIR="${PROJECT_DIR}/build-universal"
CONFIG_DIR="${PROJECT_DIR}/.pyinstaller-config"
APP_DIST_PATH="${DIST_DIR}/${APP_NAME}.app"
APP_OUT_PATH="${PROJECT_DIR}/${APP_NAME} (Standalone).app"
ZIP_OUT_PATH="${PROJECT_DIR}/${APP_NAME} (Standalone).zip"

if [[ ! -f "${PROJECT_DIR}/hello.py" ]]; then
  echo "hello.py not found in ${PROJECT_DIR}"
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

if [[ ! -x "${VENV_DIR}/bin/pyinstaller" ]]; then
  "${VENV_DIR}/bin/pip" install pyinstaller
fi

PYINSTALLER_CONFIG_DIR="${CONFIG_DIR}" "${VENV_DIR}/bin/pyinstaller" \
  --noconfirm \
  --clean \
  --windowed \
  --target-arch universal2 \
  --name "${APP_NAME}" \
  --distpath "${DIST_DIR}" \
  --workpath "${WORK_DIR}" \
  "${PROJECT_DIR}/hello.py"

rm -rf "${APP_OUT_PATH}"
cp -R "${APP_DIST_PATH}" "${APP_OUT_PATH}"

# Clear quarantine/provenance flags on bundled files and re-sign deeply.
xattr -cr "${APP_OUT_PATH}" || true
codesign --force --deep --sign - --timestamp=none "${APP_OUT_PATH}"

# Create a transfer-safe zip (preserves bundle metadata/symlinks better across machines).
rm -f "${ZIP_OUT_PATH}"
ditto -c -k --sequesterRsrc --keepParent "${APP_OUT_PATH}" "${ZIP_OUT_PATH}"

echo "Built standalone app at:"
echo "${APP_OUT_PATH}"
echo "Transfer-ready zip:"
echo "${ZIP_OUT_PATH}"
