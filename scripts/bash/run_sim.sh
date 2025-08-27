#!/bin/bash
set -e
source ~/.zshrc   # optional, only if PATH setup is needed

PROJECT_DIR="~/Workbench/Flutter  "
cd "$PROJECT_DIR"

# Simulator name you want to run on
SIMULATOR_NAME="iPhone 16 Pro (mobile)"

# Extract device ID (between the first and second •)
SIMULATOR_ID=$(flutter devices | grep "$SIMULATOR_NAME" | awk -F '•' '{print $2}' | xargs)

if [[ -z "$SIMULATOR_ID" ]]; then
  echo "❌ Simulator '$SIMULATOR_NAME' not found. Available simulators are:"
  flutter devices
  exit 1
fi

echo "🖥 Launching app on Simulator: $SIMULATOR_NAME ($SIMULATOR_ID)..."
flutter run -d "$SIMULATOR_ID"
