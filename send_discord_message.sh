#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  source .env
else
  echo "Error: .env file not found"
  exit 1
fi

# Check if WEBHOOK_URL is set
if [ -z "$WEBHOOK_URL" ]; then
  echo "Error: WEBHOOK_URL is not set in .env file"
  exit 1
fi

if [ -z "$1" ]; then
  echo "Usage: $0 \"Your message here\""
  exit 1
fi

MESSAGE="$1"

curl -H "Content-Type: application/json" \
     -X POST \
     -d "{\"content\": \"$MESSAGE\", \"username\": \"Custom Name\"}" \
     "$WEBHOOK_URL"