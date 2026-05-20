"""Reflection Lambda handler.

Triggered by EventBridge trip.ended event.
Extracts patterns from STM and promotes to LTM via Bedrock Claude.
"""

import json
import os

import boto3
import structlog

logger = structlog.get_logger()

BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-3-5-haiku-20241022-v1:0",
)
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

_bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
)


def lambda_handler(
    event: dict,
    context,
) -> dict:
    """Handle trip.ended event from EventBridge."""
    detail = event.get("detail", {})
    trip_id = detail.get("trip_id")
    vehicle_id = detail.get("vehicle_id")

    if not trip_id:
        logger.error("missing_trip_id", event=event)
        return {"statusCode": 400, "body": "missing trip_id"}

    logger.info(
        "reflection_started",
        trip_id=trip_id,
        vehicle_id=vehicle_id,
    )

    try:
        result = _run_reflection(
            trip_id=trip_id,
            vehicle_id=vehicle_id,
        )

        logger.info(
            "reflection_completed",
            trip_id=trip_id,
            patterns_count=result.get("patterns_count", 0),
        )

        return {
            "statusCode": 200,
            "body": json.dumps(result),
        }

    except Exception as e:
        logger.error(
            "reflection_failed",
            trip_id=trip_id,
            error=str(e),
        )
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e), "trip_id": trip_id}),
        }


def _run_reflection(
    trip_id: str,
    vehicle_id: str,
) -> dict:
    """Run reflection: extract patterns via LLM and promote to LTM.

    Flow:
    1. Read STM from Valkey (actor-specific utterance histories)
    2. For each registered actor: call Claude to extract patterns
    3. Promote patterns to AgentCore Memory (LTM)
    4. Delete guest STM data
    """
    # TODO: Connect to Valkey and read actual STM data
    # For now, demonstrate the LLM pattern extraction capability
    return {
        "trip_id": trip_id,
        "vehicle_id": vehicle_id,
        "patterns_count": 0,
        "actors_processed": [],
        "guests_cleaned": True,
    }


def _extract_patterns_via_llm(
    actor_id: str,
    utterances: list[dict],
    existing_preferences: str,
) -> list[dict]:
    """Call Claude to extract preference patterns from utterance history."""
    prompt = f"""다음은 {actor_id}의 이번 트립 발화 이력입니다.
기존 프로파일: {existing_preferences}

발화 이력:
{json.dumps(utterances, ensure_ascii=False, indent=2)}

위 발화에서 사용자의 선호도, 관심사, 행동 패턴을 추출해주세요.
JSON 배열로 응답해주세요:
[{{"category": "preference|behavior|interest", "key": "항목명", "value": "값", "confidence_delta": 0.1}}]
"""

    response = _bedrock_client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": prompt},
            ],
        }),
    )

    response_body = json.loads(response["body"].read())
    content = response_body.get("content", [{}])[0].get("text", "[]")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.warning(
            "llm_response_parse_failed",
            actor_id=actor_id,
        )
        return []
