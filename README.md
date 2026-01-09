# Private Docker Registry Admin API (Flask)

![Type](https://img.shields.io/badge/Type-Platform%20Tool-informational?style=flat-square)
![Service](https://img.shields.io/badge/Service-Docker%20Registry%20%2B%20Admin%20API-success?style=flat-square)
![Auth](https://img.shields.io/badge/Auth-htpasswd%20Basic%20Auth-blue?style=flat-square)
![Logging](https://img.shields.io/badge/Audit-audit.log-9cf?style=flat-square)

Distribution Registry(registry:2) 위에 **관리용 Flask API**를 얹어,
- htpasswd 기반 사용자 관리(추가/조회/삭제)
- 레지스트리 Catalog/Tags 조회
- audit.log 기반 감사로그(이력 추적)

를 실습/구현한 프로젝트입니다.

> 운영 관점(접근통제/감사로그/재현 가능한 실행)을 학습 목표로 했습니다.

---

## 🧩 Architecture

```mermaid
flowchart LR
  C[Client / Operator] -->|REST API| A[Admin API (Flask)\n:5001]
  A -->|Registry API 호출| R[Docker Registry (registry:2)\n:5000]
  A --> H[htpasswd\n(Basic Auth user DB)]
  A --> L[audit.log\n(Activity Audit)]
  R --> D[(Registry Storage\n./data)]
```

- `registry:2` : Docker Registry (port 5000)
- `Flask API` : Admin API (port 5001)
- `auth/htpasswd` : Basic Auth 사용자 DB
- `logs/audit.log` : API 호출 이력 로그

---

## ✨ Features

- User management via htpasswd: Add / List / Delete
- Registry browsing: Catalog / Tags
- Audit logging: 모든 주요 작업을 `audit.log`에 기록하고 사용자/이미지 기준 조회 지원
- Docker Compose 기반으로 Registry + API 서버를 손쉽게 재현 가능

---

## 🚀 Run (Docker Compose)

```bash
mkdir -p auth logs data
docker compose up -d --build
```
- Registry: http://localhost:5000
- API: http://localhost:5001

---

## ⚙️ Environment Variables
| Name             | Default                | Description        |
| ---------------- | ---------------------- | ------------------ |
| `REGISTRY_URL`   | `http://registry:5000` | Registry 내부 접근 URL |
| `HTPASSWD_PATH`  | `/auth/htpasswd`       | htpasswd 파일 경로     |
| `AUDIT_LOG_PATH` | `/logs/audit.log`      | 감사로그 경로            |

---

## 🔌 API Endpoints

| Category | Method | Path | Description |
|---|---:|---|---|
| Users | POST | `/users` | 사용자 추가 (htpasswd) |
| Users | GET | `/users` | 사용자 목록 조회 |
| Users | DELETE | `/users/<user>` | 사용자 삭제 |
| Images | GET | `/images` | 레지스트리 이미지 목록(catalog) |
| Images | GET | `/images/<name>/tags` | 특정 이미지 태그 조회 |
| Tags | DELETE | `/images/<name>/tags/<tag>` | 태그 삭제 |
| Audit | GET | `/audit?user=<user>` | 사용자별 로그 조회 |
| Audit | GET | `/audit?image=<image>` | 이미지별 로그 조회 |

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
