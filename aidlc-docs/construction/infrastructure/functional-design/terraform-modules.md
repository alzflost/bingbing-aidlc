# Terraform Modules Design — Unit 1 (Infrastructure)

## 모듈 구조

```
terraform/
├── modules/
│   ├── vpc/              # VPC + Subnets + NAT + IGW
│   ├── ecs/              # Cluster + Services + Task Defs
│   ├── elasticache/      # Valkey (IAM auth)
│   ├── dynamodb/         # vehicle_profiles
│   ├── agentcore/        # Memory Store + Policy Store + Evaluations
│   ├── lambda/           # Reflection Lambda
│   ├── eventbridge/      # trip.ended rule
│   └── alb/              # ALB + TLS + Target Groups
├── environments/
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── terraform.tfvars
├── main.tf               # 모듈 호출
├── variables.tf
├── outputs.tf
└── versions.tf
```

## 모듈별 리소스

### vpc/
| 리소스 | 설명 |
|---|---|
| aws_vpc | 메인 VPC (10.0.0.0/16) |
| aws_subnet (public x2) | ALB용 퍼블릭 서브넷 (AZ 2개) |
| aws_subnet (private x2) | ECS + ElastiCache용 프라이빗 서브넷 |
| aws_internet_gateway | 퍼블릭 서브넷 인터넷 접근 |
| aws_nat_gateway | 프라이빗 서브넷 아웃바운드 |
| aws_route_table | 퍼블릭/프라이빗 라우팅 |

### ecs/
| 리소스 | 설명 |
|---|---|
| aws_ecs_cluster | 메인 클러스터 |
| aws_ecs_task_definition (api) | API Service 태스크 (CPU/Memory, 컨테이너 정의) |
| aws_ecs_task_definition (agent) | Agent Service 태스크 |
| aws_ecs_service (api) | API Service (desired_count, ALB 연결) |
| aws_ecs_service (agent) | Agent Service (service discovery) |
| aws_service_discovery_namespace | 내부 서비스 디스커버리 (agent.local) |
| aws_iam_role (task_execution) | ECS 태스크 실행 역할 |
| aws_iam_role (task) | ECS 태스크 역할 (Bedrock, Transcribe, Valkey, DDB 접근) |
| aws_security_group (ecs) | ECS 서비스 보안 그룹 |
| aws_cloudwatch_log_group | 서비스별 로그 그룹 |

### elasticache/
| 리소스 | 설명 |
|---|---|
| aws_elasticache_serverless_cache | Valkey 서버리스 (IAM 인증 모드) |
| aws_security_group (valkey) | Valkey 보안 그룹 (ECS만 접근) |

> IAM 인증: `transit_encryption_enabled = true`, `user_group_id` 미사용, ECS Task Role에 `elasticache:Connect` 권한 부여

### dynamodb/
| 리소스 | 설명 |
|---|---|
| aws_dynamodb_table (vehicle_profiles) | PK: vehicle_id, SK: actor_id |

```hcl
resource "aws_dynamodb_table" "vehicle_profiles" {
  name         = "vehicle-profiles"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "vehicle_id"
  range_key    = "actor_id"
  
  attribute {
    name = "vehicle_id"
    type = "S"
  }
  attribute {
    name = "actor_id"
    type = "S"
  }
  
  point_in_time_recovery { enabled = true }
  server_side_encryption { enabled = true }
}
```

### agentcore/
| 리소스 | 설명 |
|---|---|
| aws_bedrockagent_agent | Strands Agent 정의 (있을 경우) |
| aws_verifiedpermissions_policy_store | CEDAR 정책 스토어 |
| aws_verifiedpermissions_policy (N개) | 각 CEDAR 정책 규칙 |
| aws_verifiedpermissions_schema | 정책 스키마 (Role, Action, Resource) |

> AgentCore Memory: Terraform provider 지원 여부에 따라 `aws_bedrockagent_agent_memory` 또는 custom provider 사용. 미지원 시 `terraform-provider-shell`로 AWS CLI 래핑.

### lambda/
| 리소스 | 설명 |
|---|---|
| aws_lambda_function | Reflection Lambda (Python 3.12, 5분 타임아웃) |
| aws_iam_role (lambda) | Lambda 실행 역할 (Valkey, AgentCore Memory, Bedrock 접근) |
| aws_lambda_permission | EventBridge 호출 허용 |
| aws_cloudwatch_log_group | Lambda 로그 |

### eventbridge/
| 리소스 | 설명 |
|---|---|
| aws_cloudwatch_event_rule | trip.ended 이벤트 패턴 |
| aws_cloudwatch_event_target | Lambda 타겟 |

### alb/
| 리소스 | 설명 |
|---|---|
| aws_lb | Application Load Balancer |
| aws_lb_listener (443) | HTTPS 리스너 (ACM 인증서) |
| aws_lb_target_group (api) | API Service 타겟 그룹 |
| aws_security_group (alb) | ALB 보안 그룹 (80/443 인바운드) |
| aws_acm_certificate | TLS 인증서 |

## IAM 최소 권한 (SECURITY-06)

### ECS Task Role (API Service)
```json
{
  "Effect": "Allow",
  "Action": [
    "transcribe:StartStreamTranscription",
    "elasticache:Connect",
    "dynamodb:GetItem", "dynamodb:Query",
    "events:PutEvents"
  ],
  "Resource": ["specific ARNs"]
}
```

### ECS Task Role (Agent Service)
```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "elasticache:Connect",
    "dynamodb:GetItem", "dynamodb:Query", "dynamodb:PutItem",
    "verifiedpermissions:IsAuthorized"
  ],
  "Resource": ["specific ARNs"]
}
```

### Lambda Role (Reflection)
```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "elasticache:Connect",
    "dynamodb:GetItem", "dynamodb:PutItem"
  ],
  "Resource": ["specific ARNs"]
}
```
