# Frontend Components — Unit 5 (React + TypeScript + Zustand)

## 컴포넌트 계층

```
App
├── TripProvider (WebSocket 연결 관리)
├── Layout
│   ├── Header (트립 상태, 연결 상태)
│   ├── MainPanel
│   │   ├── SeatMap (좌석 배치도)
│   │   ├── ConversationStream (대화 스트림)
│   │   └── DriverAuth (운전자 프로필 선택)
│   └── SidePanel
│       ├── PermissionDashboard (권한 매트릭스)
│       ├── MemoryPanel (STM/LTM 상태)
│       └── EvaluationPanel (지표 차트)
```

## 핵심 컴포넌트

### SeatMap
- 차량 좌석 4개 시각화 (운전석, 조수석, 뒷좌석L, 뒷좌석R)
- 각 좌석에 탑승자 이름 + 역할 속성 배지 표시
- 점유/비점유 상태 색상 구분
- 현재 발화 중인 좌석 하이라이트
- 좌석 클릭 → 해당 탑승자 상세 정보 팝업

### ConversationStream
- 실시간 대화 표시 (채팅 형태)
- 페르소나별 색상 구분 (driver=파랑, child=초록, elder=보라, guest=회색)
- 시스템 응답 vs 사용자 발화 구분
- 정책 차단 시 빨간 배지 + 거절 사유 표시
- 동시 발화 큐잉 상태 표시 (대기 중 발화 dim 처리)

### DriverAuth
- 트립 시작 시 표시 (시동 ON 이벤트)
- 차량 등록 프로필 목록 (DDB에서 조회)
- 프로필 카드 선택 → 운전자 확정
- 확정 후 자동 숨김

### PermissionDashboard
- 현재 탑승자별 권한 매트릭스 테이블
- 도구별 허용/차단/조건부 아이콘
- 실시간 정책 평가 결과 로그

### MemoryPanel
- STM: 현재 트립 발화 이력 (actor별 탭)
- LTM: 선호도 요약 (AgentCore Memory에서 조회)
- Reflection 결과 (트립 종료 후)

### EvaluationPanel (P2)
- 화자 식별 정확도 게이지
- 페르소나 일관성 게이지
- 가드레일 누락률 게이지
- 트립별 추이 라인 차트

## Zustand Stores

### tripStore
```typescript
interface TripState {
  tripId: string | null
  vehicleId: string
  state: 'idle' | 'onboarding' | 'active' | 'trip_end'
  seatOccupancy: Record<number, ActorInfo | null>
  driverActorId: string | null
  speakerMappings: Record<string, string>  // spk_label → actor_id
  
  // Actions
  startTrip: (vehicleId: string, seatData: SeatOccupancy) => void
  endTrip: () => void
  updateMapping: (spkLabel: string, actorId: string) => void
  updateState: (state: MappingState) => void
}
```

### conversationStore
```typescript
interface ConversationState {
  messages: ConversationMessage[]
  pendingQueue: QueuedUtterance[]  // 동시 발화 큐
  
  // Actions
  addMessage: (msg: ConversationMessage) => void
  addToQueue: (utterance: QueuedUtterance) => void
  removeFromQueue: (id: string) => void
}
```

### profileStore
```typescript
interface ProfileState {
  vehicleProfiles: VehicleProfile[]
  currentPermissions: Record<string, PermissionSet>
  memoryState: Record<string, MemorySnapshot>
  
  // Actions
  loadProfiles: (vehicleId: string) => void
  updatePermissions: (actorId: string, perms: PermissionSet) => void
}
```

## WebSocket 메시지 핸들링

```typescript
// hooks/useWebSocket.ts
function useWebSocket(tripId: string) {
  // 수신 메시지 라우팅
  onMessage(type: 'transcription') → conversationStore.addMessage()
  onMessage(type: 'agent_response') → conversationStore.addMessage()
  onMessage(type: 'mapping_update') → tripStore.updateMapping()
  onMessage(type: 'state_update') → tripStore.updateState()
  
  // 송신
  sendAudio(chunk: ArrayBuffer) → ws.send({type: 'audio_chunk', data})
  sendTripStart(vehicleId, seatData, driverActorId) → ws.send({type: 'trip_start', ...})
  sendTripEnd() → ws.send({type: 'trip_end'})
}
```

## 좌석 센서 목업

```typescript
// components/SeatMap에서 좌석 클릭으로 점유 시뮬레이션
// 실제 차량에서는 CAN bus 데이터 → 여기서는 UI 클릭으로 대체
function toggleSeatOccupancy(channel: number) {
  // 좌석 점유/비점유 토글
  // 점유 시 → 미매핑 상태로 표시 (매핑 대기)
}
```
