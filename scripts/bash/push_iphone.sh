#!/bin/bash
set -e
source ~/.zshrc   # optional, only if PATH setup is needed

PROJECT_DIR="/Users/thyagil/Amrutham/Flutter/srimad_ramayanam"
cd "$PROJECT_DIR"

DEVICE_NAME="Thyagi’s iPhone"

# Extract device ID from flutter devices (between the first and second •)
DEVICE_ID=$(flutter devices | grep "$DEVICE_NAME" | awk -F '•' '{print $2}' | xargs)

if [[ -z "$DEVICE_ID" ]]; then
  echo "❌ Device '$DEVICE_NAME' not found. Available devices are:"
  flutter devices
  exit 1
fi

echo "✅ Found device: $DEVICE_NAME ($DEVICE_ID)"
echo "🚀 Building Flutter app for iOS (release)..."
# flutter build ios --release

echo "📲 Installing app onto iPhone..."
# ios-deploy --id "$DEVICE_ID" --bundle build/ios/iphoneos/Runner.app

flutter run -d "$DEVICE_ID"
