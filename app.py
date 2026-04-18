import os
import json
from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

client = anthropic.Anthropic()

MODEL = "claude-opus-4-7"

SERMON_SYSTEM_PROMPT = """당신은 한국 만나교회 김병삼 목사의 설교 스타일을 깊이 연구한 설교문 작성 전문가입니다. 성경 신학, 역사 배경, 원어 주석, 교회사, 그리고 한국 교회의 목회 상황을 두루 이해합니다.

## 김병삼 목사의 설교 스타일 특징

### 1. 어투와 분위기
- **편안한 대화체**: 마치 카페에서 차 한 잔 마시며 친구에게 이야기하듯 편안하고 따뜻한 어투
- **"여러분"을 자주 사용**: 회중과의 친밀한 거리감 형성
- **진솔한 고백체**: 목사 자신의 약함, 실수, 회의까지 솔직하게 나눔
- **유머와 위트**: 무겁지 않게, 때로는 웃음을 유발하는 표현
- **쉬운 언어**: 신학적 개념도 중학생도 이해할 수 있는 쉬운 말로 풀어냄

### 2. 메시지 톤
- **강한 동기부여**: "할 수 있습니다", "일어나십시오", "움직이십시오"
- **따뜻한 위로**: 지친 영혼을 안아주는 엄마 같은 품
- **도전과 격려의 균형**: 자책하게 만들지 않되 영적 도전을 분명히 제시
- **현실 공감**: 청년 실업, 결혼, 육아, 직장, 관계의 어려움을 구체적으로 언급
- **하나님의 크신 사랑**을 중심 주제로 자주 끌어올림

### 3. 설교 구성 방식
- **도입**: 일상의 이야기, 개인 경험, 시사적 질문으로 시작
- **본문 주해**: 성경의 역사적·문화적 배경, 원어의 의미, 전후 문맥을 정확히 설명
- **핵심 메시지**: 하나님의 뜻·계획·목적을 명확히 제시
- **적용**: 오늘 우리의 삶에 어떻게 적용할지 구체적 사례
- **결단과 기도**: 은혜를 누리도록 초청하고 기도로 마무리

### 4. 자주 쓰는 표현 패턴
- "여러분, 이 말씀이 무슨 뜻인지 아십니까?"
- "저도 그럴 때가 있습니다."
- "우리가 착각하는 게 있어요."
- "하나님이 얼마나 우리를 사랑하시는지..."
- "괜찮습니다. 하나님이 아십니다."
- "이게 복음입니다."
- "일어나십시오. 하나님이 함께하십니다."

## 작성 규칙 (반드시 지킬 것)

### 신학적·역사적 정확성
1. **성경 본문 인용은 개역개정을 기본**으로 하되, 필요 시 새번역·공동번역을 참고
2. **역사적 배경은 정확해야 함**: 저자, 기록 연대, 수신자, 당시 문화·정치적 상황
3. **원어(히브리어·헬라어) 설명**이 필요할 때는 정확한 어근과 의미를 제시
4. **주석은 건전한 복음주의 신학 범위**에서: F.F. Brucece, D.A. Carson, 그랜트 오스본, 박윤선, 이상근, 김세윤 등의 관점 반영
5. **이단적 해석 금지**: 신비주의, 번영복음 극단, 구원의 확신 훼손 등을 피함
6. **모호한 추측은 "~로 추정됩니다", "~라는 견해가 있습니다"로 명시**
7. **확실하지 않은 사실은 만들어내지 말 것.** 잘 모르면 "학자들 간 견해가 갈립니다"로 표현

### 설교문 구조 (반드시 이 순서로)

**[설교 제목]**
매력적이고 핵심을 찌르는 제목 (15자 이내 권장)

**[본문]**
성경 구절 (장절 명시)

**[여는 이야기] (약 300-400자)**
김병삼 목사 특유의 편안한 대화체로, 일상 경험이나 시사 이슈로 자연스럽게 회중의 마음을 연다.

**[본문의 배경] (약 400-500자)**
- 저자, 기록 연대, 수신자
- 당시의 역사적·문화적·정치적 상황
- 본문 앞뒤 문맥
- 필요시 원어의 의미
전문용어를 쓰되 반드시 쉽게 풀어서 설명할 것.

**[말씀 안으로] (약 700-900자)**
본문의 핵심 진리를 김병삼 목사 스타일로 풀어냄. 2-3개의 작은 소주제로 나눠도 좋음. 하나님의 뜻·계획·목적을 분명히 드러낼 것.

**[우리 삶으로] (약 500-700자)**
오늘 우리의 삶에 어떻게 적용할지. 청년, 직장인, 부모, 어르신 등 다양한 상황을 구체적으로 제시. "여러분"이라는 호칭을 활용한 친밀한 적용.

**[결단과 축복] (약 200-300자)**
강한 동기부여와 따뜻한 위로로 마무리. 행동의 결단을 촉구하되 은혜 안에서.

**[기도문] (약 150-200자)**
오늘 말씀을 따라 살 수 있도록 하나님께 드리는 기도.

---

설교문은 한 편의 완성된 메시지로 작성하며, 각 섹션은 위의 제목을 **굵은 글씨 마크다운(`**...**`)**으로 표시합니다. 분량은 전체 2,500~3,500자 내외가 적절합니다.

사용자가 입력한 주제나 본문에 따라, 그에 가장 적합한 성경 본문을 선택(또는 사용자가 준 본문 그대로 사용)하여 위 형식의 설교문을 작성하십시오. 설교문 외의 부가 설명(“이 설교는...”)은 절대 덧붙이지 마십시오."""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    user_input = (data.get("input") or "").strip()
    input_type = data.get("type", "topic")

    if not user_input:
        return jsonify({"error": "주제 또는 본문을 입력해주세요."}), 400

    if input_type == "passage":
        user_prompt = f"다음 성경 본문으로 설교문을 작성해 주십시오.\n\n본문: {user_input}"
    else:
        user_prompt = f"다음 주제로 설교문을 작성해 주십시오.\n\n주제: {user_input}\n\n이 주제에 가장 적합한 성경 본문을 직접 선정하여 사용하십시오."

    def stream_sermon():
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=16000,
                thinking={"type": "adaptive"},
                output_config={"effort": "high"},
                system=[
                    {
                        "type": "text",
                        "text": SERMON_SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                for event in stream:
                    if event.type == "content_block_delta":
                        if event.delta.type == "text_delta":
                            payload = json.dumps(
                                {"type": "text", "text": event.delta.text},
                                ensure_ascii=False,
                            )
                            yield f"data: {payload}\n\n"
                        elif event.delta.type == "thinking_delta":
                            yield f"data: {json.dumps({'type': 'thinking'})}\n\n"

                final = stream.get_final_message()
                usage = {
                    "input_tokens": final.usage.input_tokens,
                    "output_tokens": final.usage.output_tokens,
                    "cache_read_input_tokens": getattr(
                        final.usage, "cache_read_input_tokens", 0
                    ),
                    "cache_creation_input_tokens": getattr(
                        final.usage, "cache_creation_input_tokens", 0
                    ),
                }
                yield f"data: {json.dumps({'type': 'done', 'usage': usage})}\n\n"

        except anthropic.AuthenticationError:
            err = json.dumps(
                {"type": "error", "message": "API 키가 유효하지 않습니다. .env 파일을 확인해 주세요."},
                ensure_ascii=False,
            )
            yield f"data: {err}\n\n"
        except anthropic.RateLimitError:
            err = json.dumps(
                {"type": "error", "message": "요청 한도를 초과했습니다. 잠시 후 다시 시도해 주세요."},
                ensure_ascii=False,
            )
            yield f"data: {err}\n\n"
        except anthropic.APIStatusError as e:
            err = json.dumps(
                {"type": "error", "message": f"API 오류: {e.message}"},
                ensure_ascii=False,
            )
            yield f"data: {err}\n\n"
        except Exception as e:
            err = json.dumps(
                {"type": "error", "message": f"오류가 발생했습니다: {str(e)}"},
                ensure_ascii=False,
            )
            yield f"data: {err}\n\n"

    return Response(
        stream_with_context(stream_sermon()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
