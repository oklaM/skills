#!/bin/bash
# generate_code.sh — Generate a random OTC confirmation code
# Usage: bash generate_code.sh [prefix] [length]
# Default: cf-XXXX (prefix="cf", length=4)

PREFIX="${1:-cf}"
LENGTH="${2:-4}"
CHARS="abcdefghijklmnopqrstuvwxyz0123456789"

CODE=""
for i in $(seq 1 "$LENGTH"); do
  RAND_INDEX=$((RANDOM % ${#CHARS}))
  CODE="${CODE}${CHARS:$RAND_INDEX:1}"
done

echo "${PREFIX}-${CODE}"
