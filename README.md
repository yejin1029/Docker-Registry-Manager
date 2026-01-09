# Private Docker Registry Admin API (Flask)

Distribution Registry(registry:2) 위에 **관리용 Flask API**를 얹어,
- htpasswd 기반 사용자 관리(추가/조회/삭제)
- 레지스트리 Catalog/Tags 조회
- audit.log 기반 감사로그(이력 추적)

를 실습/구현한 프로젝트입니다.

> 운영 관점(접근통제/감사로그/재현 가능한 실행)을 학습 목표로 했습니다.

---

## Architecture

- `registry:2` : Docker Registry (port 5000)
- `Flask API` : Admin API (port 5001)
- `auth/htpasswd` : Basic Auth 사용자 DB
- `logs/audit.log` : API 호출 이력 로그

---

## Run (Docker Compose)

```bash
mkdir -p auth logs data
docker compose up -d --build
```
- Registry: http://localhost:5000
- API: http://localhost:5001

---

## Environment Variables
| Name             | Default                | Description        |
| ---------------- | ---------------------- | ------------------ |
| `REGISTRY_URL`   | `http://registry:5000` | Registry 내부 접근 URL |
| `HTPASSWD_PATH`  | `/auth/htpasswd`       | htpasswd 파일 경로     |
| `AUDIT_LOG_PATH` | `/logs/audit.log`      | 감사로그 경로            |

---

## API Endpoints

### Add user
```bash
curl -X POST http://localhost:5001/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test1234"}'
```

### List users
```bash
curl http://localhost:5001/users
```

### Delete user
```bash
curl -X DELETE http://localhost:5001/users/test
```

### Registry catalog
```bash
curl http://localhost:5001/images
```

### Image tags
```bash
curl http://localhost:5001/images/<repo>/tags
```

---

## Audit Log
- 기록 파일: logs/audit.log
- 사용자/이미지 기준 필터 조회 API 제공

## Security Notes
- docker.sock 마운트는 매우 강한 권한을 부여합니다.
- 본 프로젝트는 학습/실습 목적이며, 운영 환경 적용 시 별도 보안 설계가 필요합니다.

## Known Limitations / TODO
- 이미지 삭제는 Registry API(digest 기반 삭제)로 정교화 필요
- Auth 적용 범위/권한(Role) 분리 필요
- API 인증/인가(JWT 등) 및 rate limit 고려 가능
