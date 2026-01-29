"""
📁 File: src/interfaces/http/routes/chat.py
Layer: Interfaces (HTTP)
Purpose: Smart chat endpoint with intelligent model routing
Depends on: src/layer0_model_infra
Used by: Clients

This endpoint demonstrates the platform's core differentiator:
- Automatically selects the optimal model based on query
- Minimizes costs while maintaining quality
- Provides transparency on routing decisions
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.layer0_model_infra.gateway import LLMRequest, get_gateway
from src.layer0_model_infra.router import get_router
from src.shared.errors import ModelError, ModelNotFoundError
from src.shared.logger import get_logger

# Initialize
router = APIRouter(prefix="/chat", tags=["Chat"])
logger = get_logger(__name__)
model_router = get_router()
gateway = get_gateway()


class ChatRequest(BaseModel):
    """Request for smart chat endpoint."""
    
    message: str = Field(..., description="User's message", min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, description="Max output tokens")
    force_model_id: Optional[str] = Field(
        None, description="Force specific model (bypasses routing)"
    )
    has_images: bool = Field(default=False, description="Whether images are attached")
    has_audio: bool = Field(default=False, description="Whether audio is attached")


class ChatResponse(BaseModel):
    """Response from smart chat endpoint."""
    
    response: str = Field(..., description="AI response")
    model_used: str = Field(..., description="Model that generated response")
    routing_decision: dict = Field(..., description="Why this model was selected")
    cost: dict = Field(..., description="Cost information")
    performance: dict = Field(..., description="Performance metrics")


@router.post(
    "",
    response_model=ChatResponse,
    summary="Smart Chat",
    description="Chat endpoint with intelligent model routing for cost optimization",
)
async def smart_chat(request: ChatRequest) -> ChatResponse:
    """
    Smart chat endpoint with automatic model selection.
    
    This is the CORE DIFFERENTIATOR:
    - Analyzes query complexity, intent, and modality
    - Automatically selects the most cost-effective model
    - Uses Ollama (free) for simple queries
    - Uses premium models only when needed
    
    Args:
        request: Chat request with message and options
        
    Returns:
        Chat response with model routing transparency
        
    Raises:
        HTTPException: If routing or generation fails
    """
    logger.info(
        "smart_chat_request_received",
        message_length=len(request.message),
        force_model=request.force_model_id,
    )
    
    try:
        # Step 1: Route the query to optimal model
        routing_decision = model_router.route(
            query=request.message,
            has_images=request.has_images,
            has_audio=request.has_audio,
            force_model_id=request.force_model_id,
        )
        
        selected_model = routing_decision.selected_model
        
        logger.info(
            "model_routed",
            selected_model_id=selected_model.model_id,
            complexity=routing_decision.query_analysis.complexity,
            estimated_cost=routing_decision.estimated_cost_usd,
        )
        
        # Step 2: Generate response using selected model
        llm_request = LLMRequest(
            model_id=selected_model.model_id,
            messages=[{"role": "user", "content": request.message}],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        llm_response = await gateway.complete(llm_request)
        
        # Step 3: Build transparent response
        return ChatResponse(
            response=llm_response.content,
            model_used=selected_model.display_name,
            routing_decision={
                "reasoning": routing_decision.reasoning,
                "complexity": routing_decision.query_analysis.complexity,
                "intent": routing_decision.query_analysis.intent,
                "reasoning_score": routing_decision.query_analysis.reasoning_score,
                "fallback_models": [
                    m.display_name for m in routing_decision.fallback_models
                ],
            },
            cost={
                "actual_cost_usd": llm_response.cost_usd,
                "estimated_cost_usd": routing_decision.estimated_cost_usd,
                "provider": selected_model.provider,
                "is_free": llm_response.cost_usd == 0.0,
            },
            performance={
                "latency_ms": llm_response.latency_ms,
                "input_tokens": llm_response.input_tokens,
                "output_tokens": llm_response.output_tokens,
                "total_tokens": llm_response.total_tokens,
            },
        )
    
    except ModelNotFoundError as e:
        logger.error("model_not_found", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model not found: {e.message}",
        )
    
    except ModelError as e:
        logger.error("model_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model error: {e.message}",
        )
    
    except Exception as e:
        logger.error(
            "smart_chat_failed",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}",
        )


@router.post(
    "/analyze",
    summary="Analyze Query",
    description="Analyze a query to see routing decision without generating response",
)
async def analyze_query(
    message: str,
    has_images: bool = False,
    has_audio: bool = False,
) -> dict:
    """
    Analyze a query to see which model would be selected.
    
    Useful for understanding and testing the routing logic.
    
    Args:
        message: User's message
        has_images: Whether images are attached
        has_audio: Whether audio is attached
        
    Returns:
        Routing decision with selected model and reasoning
    """
    try:
        routing_decision = model_router.route(
            query=message,
            has_images=has_images,
            has_audio=has_audio,
        )
        
        return {
            "selected_model": {
                "id": routing_decision.selected_model.model_id,
                "name": routing_decision.selected_model.display_name,
                "provider": routing_decision.selected_model.provider,
            },
            "reasoning": routing_decision.reasoning,
            "query_analysis": {
                "complexity": routing_decision.query_analysis.complexity,
                "modality": routing_decision.query_analysis.modality,
                "intent": routing_decision.query_analysis.intent,
                "reasoning_score": routing_decision.query_analysis.reasoning_score,
                "requires_coding": routing_decision.query_analysis.requires_coding,
                "requires_creativity": routing_decision.query_analysis.requires_creativity,
            },
            "estimated_cost_usd": routing_decision.estimated_cost_usd,
            "fallback_models": [
                {
                    "id": m.model_id,
                    "name": m.display_name,
                }
                for m in routing_decision.fallback_models
            ],
        }
    
    except Exception as e:
        logger.error("query_analysis_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )
