#!/bin/bash
# .env.local의 SERVER_PORT를 8004로 업데이트

ENV_FILE=".env.local"

if [ -f "$ENV_FILE" ]; then
    # SERVER_PORT가 있으면 업데이트, 없으면 추가
    if grep -q "^SERVER_PORT=" "$ENV_FILE"; then
        sed -i 's/^SERVER_PORT=.*/SERVER_PORT=8004/' "$ENV_FILE"
        echo "✅ SERVER_PORT를 8004로 업데이트했습니다"
    else
        echo "SERVER_PORT=8004" >> "$ENV_FILE"
        echo "✅ SERVER_PORT=8004를 추가했습니다"
    fi
else
    echo "❌ .env.local 파일을 찾을 수 없습니다"
    exit 1
fi

echo ""
echo "업데이트된 내용:"
grep "^SERVER_PORT=" "$ENV_FILE" || echo "SERVER_PORT 설정을 찾을 수 없습니다"
