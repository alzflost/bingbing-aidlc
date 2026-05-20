# Business Logic Model — API Service (Unit 2)

## 1. WebSocket Gateway

### 연결 흐름
```
Client Connect → JWT 검증 → vehicle_id 추출 → 세션 생성 → 연결 승인
Client Disconnect → 세션 정리 → (시동 OFF 아니면 재연결 대기)
```

### 메시지 타입 (Client → Server)
- `audio_chunk`: 오디오 바이너리 (PCM 16kHz)
- `trip_start`: 시동 ON + 좌석 점유 정보 + 운전자 actor_id
- `trip_end`: 시동 OFF
- `seat_update`: 좌석 점유 변경

### 메시지 타입 (Server → Client)
- `transcription`: 실시간 전사 결과 (spk_label + text)
- `agent_response`: 에이전트 응답 (actor_id + text + metadata)
- `mapping_update`: 화자 매핑 상태 변경
- `state_update`: 트립 상태 변경

## 2. Voice Ingestion

### Transcribe Streaming 연동
```
audio_chunk 수신
  → Transcribe Streaming 세션에 전달
  → diarization 결과 수신 (spk_label + transcript + confidence)
  → Speaker Mapping으로 전달
```

### FALLBACK 모드
- 트리거: Transcribe 연결 실패 3회 연속
- 동작: 사전 정의된 시나리오 파일에서 순차적으로 diarization 결과 생성
- 복구: 30초마다 Transcribe 재연결 시도, 성공 시 LIVE 복귀

## 3. Speaker Mapping State Machine

### 상태 전이
```
IDLE → (trip_start) → ONBOARDING
ONBOARDING → (모든 좌석 매핑 완료 또는 30초 타임아웃) → ACTIVE
ACTIVE → (trip_end) → TRIP_END
TRIP_END → (Reflection 완료) → IDLE
ACTIVE → (새 좌석 점유 감지) → ACTIVE (re-mapping 서브플로우)
```

### 매핑 알고리즘 (3단계)

**Stage 1: 좌석 채널 매핑**
```
trip_start 수신 시:
  - driver_actor_id = 운전자가 선택한 프로필
  - seat_occupancy[0] = driver_actor_id, driver=true
  - DDB에서 vehicle_id의 등록 프로필 조회
  - 각 프로필의 default_seat_channel과 현재 점유 좌석 매칭 시도
```

**Stage 2: 자기소개 바인딩**
```
미매핑 좌석에서 첫 발화 감지 시:
  - 시스템: "안녕하세요! 이름을 말씀해주시겠어요?"
  - 응답 수신 → DDB 등록 프로필 이름과 매칭
  - 매칭 성공 → 바인딩 확정
  - 매칭 실패 → Stage 3 또는 임시 프로파일 생성
```

**Stage 3: 휴리스틱**
```
발화 어휘/말투 분석:
  - 짧은 문장 + 단순 어휘 → age_group=child 추정
  - 느린 발화 + 존칭 사용 → age_group=elder 추정
  - 일반 성인 패턴 → age_group=adult
```

### 미등록 가족 처리
```
자기소개 했지만 DDB에 없는 경우:
  - Valkey STM에 임시 프로파일 저장 (이름, 추정 age_group, relationship=family)
  - 트립 동안 family 권한 부여
  - 트립 종료 시 운전자에게 확인: "OO를 가족으로 등록할까요?"
  - 승인 → DDB에 영구 등록
  - 거부 → STM에서 삭제
```

## 4. 동시 발화 버퍼링

### 버퍼링 로직
```
발화 수신 시:
  IF 현재 버퍼 없음:
    - 새 버퍼 생성, 500ms 타이머 시작
    - 발화를 버퍼에 추가
  ELSE IF 현재 버퍼 존재 (타이머 진행 중):
    - 발화를 버퍼에 추가
  
  타이머 만료 시:
    IF 버퍼에 1건 → Agent Service /agent/process 호출
    IF 버퍼에 2건+ → Agent Service /agent/concurrent 호출
    - 버퍼 초기화
```
