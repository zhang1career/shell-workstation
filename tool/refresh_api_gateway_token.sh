#!/bin/bash

# Usage check
if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <app> <redis_host> <redis_port>"
  exit 1
fi

# Arguments
APP="$1"
REDIS_HOST="$2"
REDIS_PORT="$3"
TOKEN_KEY="${APP}:apigw:token"
REFRESH_KEY="${APP}:apigw:refresh"

# Get API base URL from Redis
API_GATEWAY_BASE=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" GET "reg:serv:api-gateway")
if [ -z "$API_GATEWAY_BASE" ]; then
  echo "Error: Failed to retrieve 'reg:serv:api-gateway' from Redis."
  exit 1
fi

# Build full API URL
API_GATEWAY_URL="${API_GATEWAY_BASE}/consumer/login"

# Get refresh token
REFRESH_TOKEN=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" GET "$REFRESH_KEY")
if [ -z "$REFRESH_TOKEN" ]; then
  echo "Error: Failed to retrieve refresh token from Redis key '$REFRESH_KEY'."
  exit 1
fi

# Make the PUT request
RESPONSE=$(curl -s -X PUT "$API_GATEWAY_URL" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

# Parse the JSON response
NEW_TOKEN=$(echo "$RESPONSE" | jq -r '.token')
NEW_REFRESH_TOKEN=$(echo "$RESPONSE" | jq -r '.refresh_token')
if [ "$NEW_TOKEN" == "null" ] || [ "$NEW_REFRESH_TOKEN" == "null" ]; then
  echo "Error: Invalid response from API."
  echo "Response: $RESPONSE"
  exit 1
fi

# Save updated values to Redis
TTL_SECONDS=2592000  # 30 days in seconds
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SET "$TOKEN_KEY" "$NEW_TOKEN" EX $TTL_SECONDS > /dev/null
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SET "$REFRESH_KEY" "$NEW_REFRESH_TOKEN" EX $TTL_SECONDS > /dev/null

# Output result
echo "$APP token refreshed"
