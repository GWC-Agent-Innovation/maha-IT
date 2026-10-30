#!/usr/bin/env bash
# Single entry point to build and run the Citizen Certificate Portal in Docker.
#
# Usage:
#   ./script.sh            Build the image, start the container and open the portal
#   ./script.sh stop       Stop the container (data is kept)
#   ./script.sh restart    Restart the container
#   ./script.sh logs       Follow the container logs
#   ./script.sh status     Show container status and health
#
# Optional environment variables:
#   PORT=8090                   Host port (default 8000)
#   APPROVAL_DELAY_SECONDS=20   Seconds before an application is approved (default 90)
#   NO_BROWSER=1                Do not open the browser after starting
set -euo pipefail

cd "$(dirname "$0")"

PORT="${PORT:-8000}"
APPROVAL_DELAY_SECONDS="${APPROVAL_DELAY_SECONDS:-90}"
export PORT APPROVAL_DELAY_SECONDS
URL="http://localhost:${PORT}"

info()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
fail()  { printf '\033[1;31mError:\033[0m %s\n' "$*" >&2; exit 1; }

check_docker() {
  command -v docker >/dev/null 2>&1 || fail "Docker is not installed. Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
  docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 is not available. Update Docker Desktop."
  docker info >/dev/null 2>&1 || fail "Docker is not running. Start Docker Desktop and try again."
}

port_in_use() {
  # True if something other than our container is listening on the port.
  if docker compose ps --status running --quiet portal 2>/dev/null | grep -q .; then
    return 1
  fi
  if command -v curl >/dev/null 2>&1; then
    curl -s -o /dev/null --max-time 2 "$URL" && return 0
  fi
  return 1
}

wait_for_health() {
  info "Waiting for the portal to start..."
  for _ in $(seq 1 60); do
    if curl -sf --max-time 2 "${URL}/api/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  docker compose logs --tail 30 portal
  fail "The portal did not become healthy within 60 seconds. See the logs above."
}

open_browser() {
  [ "${NO_BROWSER:-0}" = "1" ] && return 0
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) cmd.exe //c start "" "$URL" >/dev/null 2>&1 || true ;;
    Darwin*)              open "$URL" >/dev/null 2>&1 || true ;;
    *)                    command -v xdg-open >/dev/null 2>&1 && xdg-open "$URL" >/dev/null 2>&1 || true ;;
  esac
}

start() {
  check_docker
  if port_in_use; then
    fail "Port ${PORT} is already in use. Stop the other program or run: PORT=8090 ./script.sh"
  fi
  info "Building and starting the portal (port ${PORT}, approval delay ${APPROVAL_DELAY_SECONDS}s)..."
  docker compose up -d --build
  wait_for_health
  info "Portal is running at ${URL}"
  info "Stop it with: ./script.sh stop    View logs with: ./script.sh logs"
  open_browser
}

case "${1:-start}" in
  start)   start ;;
  stop)    check_docker; info "Stopping the portal (data is kept)..."; docker compose down ;;
  restart) check_docker; docker compose restart; wait_for_health; info "Portal is running at ${URL}" ;;
  logs)    check_docker; docker compose logs -f portal ;;
  status)
    check_docker
    docker compose ps
    if curl -sf --max-time 2 "${URL}/api/health" >/dev/null 2>&1; then
      info "Healthy at ${URL}"
    else
      info "Not responding at ${URL}"
    fi
    ;;
  -h|--help|help) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//' ;;
  *) fail "Unknown command '$1'. Run ./script.sh help" ;;
esac
