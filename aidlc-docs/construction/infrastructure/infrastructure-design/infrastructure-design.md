# Infrastructure Design — All Units

## AWS 아키텍처 다이어그램

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  VPC (10.0.0.0/16)                                      │
│                                                         │
│  ┌─── Public Subnets (10.0.1.0/24, 10.0.2.0/24) ───┐  │
│  │  ALB (HTTPS:443, WSS)                            │  │
│  │  NAT Gateway                                     │  │
│  └──────────────────────────────────────────────────┘  │
│           │                                             │
│           ▼                                             │
│  ┌─── Private Subnets (10.0.10.0/24, 10.0.11.0/24) ─┐ │
│  │                                                    │ │
│  │  ┌──────────────┐    ┌──────────────┐            │ │
│  │  │ API Service  │───►│ Agent Service│            │ │
│  │  │ (Fargate)    │    │ (Fargate)    │            │ │
│  │  │ Port 8080    │    │ Port 8081    │            │ │
│  │  └──────┬───────┘    └──────┬───────┘            │ │
│  │         │                    │                    │ │
│  │         ▼                    ▼                    │ │
│  │  ┌──────────────────────────────────┐            │ │
│  │  │  ElastiCache Valkey (IAM auth)   │            │ │
│  │  │  Port 6379 (TLS)                 │            │ │
│  │  └──────────────────────────────────┘            │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘

External AWS Services (via NAT):
  ├── Amazon Transcribe Streaming
  ├── Amazon Bedrock (Claude Haiku 4.5)
  ├── AgentCore Memory
  ├── AgentCore Policy (Verified Permissions)
  ├── AgentCore Evaluations
  ├── DynamoDB (vehicle_profiles)
  ├── EventBridge → Lambda (Reflection)
  ├── CloudWatch (Logs + Metrics)
  └── X-Ray (Tracing)
```

## Security Groups

| SG | Inbound | Outbound | 용도 |
|---|---|---|---|
| sg-alb | 0.0.0.0/0:443 | sg-api:8080 | ALB → API Service |
| sg-api | sg-alb:8080 | sg-agent:8081, sg-valkey:6379, 0.0.0.0/0:443 | API Service |
| sg-agent | sg-api:8081 | sg-valkey:6379, 0.0.0.0/0:443 | Agent Service |
| sg-valkey | sg-api:6379, sg-agent:6379, sg-lambda:6379 | — | Valkey (인바운드만) |
| sg-lambda | — | sg-valkey:6379, 0.0.0.0/0:443 | Reflection Lambda |

## ECS Service Configuration

### API Service
```hcl
cpu    = 512   # 0.5 vCPU
memory = 1024  # 1 GB
desired_count = 2
health_check_path = "/health"
deployment_minimum_healthy_percent = 50
deployment_maximum_percent = 200
```

### Agent Service
```hcl
cpu    = 1024  # 1 vCPU
memory = 2048  # 2 GB (LLM 호출 컨텍스트)
desired_count = 2
health_check_path = "/health"
service_discovery = "agent.family-copilot.local"
```

## ElastiCache Valkey

```hcl
engine               = "valkey"
engine_version       = "7.2"
serverless           = true  # ElastiCache Serverless
transit_encryption   = true
iam_auth_enabled     = true  # IAM 인증 (user/password 미사용)
```

## Lambda Configuration

```hcl
runtime     = "python3.12"
timeout     = 300  # 5분
memory_size = 512
reserved_concurrent_executions = 10
```

## EventBridge Rule

```json
{
  "source": ["family-copilot.api-service"],
  "detail-type": ["trip.ended"],
  "detail": {
    "trip_id": [{"exists": true}]
  }
}
```

## ALB Configuration

- HTTPS:443 (ACM 인증서)
- WebSocket 지원 (idle timeout 3600초)
- Target Group: API Service (health check /health)
- Stickiness: WebSocket 세션 유지

## Terraform Remote State

```hcl
backend "s3" {
  bucket         = "family-copilot-tfstate"
  key            = "prod/terraform.tfstate"
  region         = "ap-northeast-2"
  dynamodb_table = "terraform-locks"
  encrypt        = true
}
```

## CloudWatch Alarms

| 알람 | 조건 | 액션 |
|---|---|---|
| API 5xx 비율 | > 5% (5분) | SNS 알림 |
| Agent 응답 지연 | P95 > 3초 (5분) | SNS 알림 |
| Valkey 메모리 | > 80% | SNS 알림 |
| Lambda 에러율 | > 10% (5분) | SNS 알림 |
| ECS 태스크 수 | < desired_count (3분) | SNS 알림 |

## 리전 및 태깅

```hcl
region = "ap-northeast-2"  # Seoul

default_tags = {
  Project     = "family-copilot"
  Environment = "prod"
  ManagedBy   = "terraform"
  Team        = "aidlc-building"
}
```
