"""
topics_router.py - Presentation router for Topic Suggestion endpoints.
Same style as routers/gemini_router.py: APIRouter + HTTPException
with friendly Vietnamese messages, no business logic here.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.topic_service import TopicService

router = APIRouter(prefix="/api/topics", tags=["topics"])


class TopicCreate(BaseModel):
    hook: str = Field(min_length=1)
    fact: str = Field(min_length=1)
    source: str = ""


@router.post("/generate")
async def api_generate_topic():
    """Ask Gemini for one new topic not in the bank (AI-suggested, unverified)."""
    try:
        return {"success": True, "topic": await TopicService.generate_topic()}
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tạo chủ đề bằng AI: {str(e)}")


@router.post("")
async def api_create_topic(payload: TopicCreate):
    """Add a new topic to the bank (id = next number, status unused)."""
    try:
        return {"success": True, "topic": TopicService.create_topic(payload.hook, payload.fact, payload.source)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi thêm chủ đề: {str(e)}")


@router.get("")
async def api_list_topics(only_unused: bool = False):
    """List topics. ?only_unused=true hides topics already used."""
    try:
        topics = TopicService.list_topics(only_unused=only_unused)
        c = TopicService.counts()
        return {"success": True, "topics": topics, **c}
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi đọc ngân hàng chủ đề: {str(e)}")


@router.get("/suggest")
async def api_suggest_topic():
    """Suggest one random unused topic, or tell the user the bank is empty."""
    try:
        topic = TopicService.suggest_topic()
        if topic is None:
            return {"success": True, "topic": None,
                    "message": "Đã dùng hết 10 chủ đề trong ngân hàng. Hãy thêm chủ đề mới vào data/topics.json."}
        return {"success": True, "topic": topic}
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi gợi ý chủ đề: {str(e)}")


@router.get("/suggest3")
async def api_suggest_three():
    """Suggest up to 3 random unused topics for the user to pick from."""
    try:
        topics = TopicService.suggest_topics(count=3)
        return {"success": True, "topics": topics}
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi gợi ý chủ đề: {str(e)}")


@router.get("/{topic_id}")
async def api_get_topic(topic_id: str):
    """Return one topic by id (07-16)."""
    try:
        return {"success": True, "topic": TopicService.get_topic(topic_id)}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Không có chủ đề id={topic_id}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/use")
async def api_mark_used(topic_id: str):
    """Mark a topic as used so it is never suggested again."""
    try:
        return {"success": True, "topic": TopicService.mark_used(topic_id, used=True)}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Không có chủ đề id={topic_id}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/unuse")
async def api_mark_unused(topic_id: str):
    """Mark a topic as unused again (undo a mistaken 'used')."""
    try:
        return {"success": True, "topic": TopicService.mark_used(topic_id, used=False)}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Không có chủ đề id={topic_id}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
