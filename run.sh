#!/bin/bash
# GameEngine-Doctor Launcher
# Launches the Uvicorn server and automatically opens the browser UI.
# When you close this terminal or press Ctrl+C, the backend shuts down cleanly.

PORT=8000
URL="http://localhost:${PORT}"

echo "Starting GameEngine-Doctor backend..."
source doctoragent/bin/activate

# Open the browser in background once the server starts
(
  until curl -s "${URL}/health" > /dev/null 2>&1; do
    sleep 0.5
  done
  echo "Opening ${URL}..."
  xdg-open "${URL}" 2>/dev/null || sensible-browser "${URL}" 2>/dev/null || x-www-browser "${URL}" 2>/dev/null
) &

# Run uvicorn
exec uvicorn app.main:app --reload --port ${PORT}
