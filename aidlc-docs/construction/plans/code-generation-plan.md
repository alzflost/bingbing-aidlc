# Code Generation Plan — All Units (병렬)

## 생성 순서 (인터페이스 우선 → 병렬)

- [ ] Phase 0: 프로젝트 초기화 (루트 pyproject.toml, 모노레포 구조)
- [ ] Phase 1: Shared Models (공통 도메인 모델 — 모든 유닛의 기반)
- [ ] Phase 2: Shared Prompts + Policies (YAML 프롬프트, CEDAR 정책)
- [ ] Phase 3: Infrastructure (Terraform 모듈)
- [ ] Phase 4: API Service (FastAPI + WebSocket + Speaker Mapping)
- [ ] Phase 5: Agent Service (Strands + Policy + Memory + Tools)
- [ ] Phase 6: Reflection Lambda
- [ ] Phase 7: Frontend (React + TypeScript + Zustand)
- [ ] Phase 8: Docker + 배포 설정 (Dockerfile, docker-compose for local dev)

## 각 Phase 상세

### Phase 0: 프로젝트 초기화
- 루트 pyproject.toml (uv workspace)
- .gitignore
- README.md

### Phase 1: Shared Models
- shared/models/ — Pydantic 모델 전체
- shared/__init__.py

### Phase 2: Shared Prompts + Policies
- shared/prompts/*.yaml (5개 프리셋)
- shared/policies/*.cedar (CEDAR 정책)

### Phase 3: Infrastructure
- terraform/modules/ (8개 모듈)
- terraform/environments/prod/

### Phase 4: API Service
- services/api-service/src/ (websocket, voice, mapping, main)
- services/api-service/tests/
- services/api-service/Dockerfile
- services/api-service/pyproject.toml

### Phase 5: Agent Service
- services/agent-service/src/ (orchestrator, policy, memory, persona, tools, main)
- services/agent-service/tests/
- services/agent-service/Dockerfile
- services/agent-service/pyproject.toml

### Phase 6: Reflection Lambda
- services/reflection-lambda/src/handler.py
- services/reflection-lambda/tests/
- services/reflection-lambda/pyproject.toml

### Phase 7: Frontend
- frontend/src/ (components, hooks, services, stores, types)
- frontend/package.json
- frontend/tsconfig.json
- frontend/vite.config.ts

### Phase 8: Docker + 배포
- docker-compose.yml (로컬 개발용)
- 각 서비스 Dockerfile
