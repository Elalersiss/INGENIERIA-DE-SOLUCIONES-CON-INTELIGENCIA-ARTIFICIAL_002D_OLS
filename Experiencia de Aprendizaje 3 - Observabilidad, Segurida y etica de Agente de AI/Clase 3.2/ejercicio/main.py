from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage
from agent_app.agent import app as agent
from agent_app.models import ChatRequest, ChatResponse
from agent_app.utils.messages import to_lc_message
import uuid
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "model": request.model,
        }
    }

    try:
        messages = [to_lc_message(m) for m in request.conversation]
        messages.append(HumanMessage(content=request.question))

        result = agent.invoke({"messages": messages}, config=config)

        answer = result["messages"][-1].content

        prompt_tokens = 0
        completion_tokens = 0
        for msg in result["messages"]:
            usage = getattr(msg, "usage_metadata", None)
            if usage:
                prompt_tokens += usage.get("input_tokens", 0)
                completion_tokens += usage.get("output_tokens", 0)

        return ChatResponse(
            answer=answer,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    except Exception as e:
        logger.error("Error in /chat: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": f"Agent error: {str(e)}"},
        )