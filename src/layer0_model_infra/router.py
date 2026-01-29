"""
📁 File: src/layer0_model_infra/router.py
Layer: Layer 0 (Model Infrastructure)
Purpose: Intelligently route queries to optimal models
Depends on: src/layer0_model_infra/query_analyzer, src/layer0_model_infra/registry
Used by: API routes, orchestrator

The router's job:
1. Analyze the query
2. Consider cost, performance, and capability requirements
3. Select the most cost-effective model that meets requirements
4. Provide fallback options

This is the CORE DIFFERENTIATOR of the platform.
"""

from typing import Optional

from pydantic import BaseModel, Field

from src.layer0_model_infra.models import ModelCapability, ModelDefinition, ModelType
from src.layer0_model_infra.query_analyzer import (
    QueryAnalysis,
    QueryComplexity,
    QueryIntent,
    QueryModality,
    get_analyzer,
)
from src.layer0_model_infra.registry import get_registry
from src.shared.config import get_settings
from src.shared.errors import ModelNotFoundError
from src.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RoutingDecision(BaseModel):
    """Decision made by the router."""
    
    selected_model: ModelDefinition = Field(..., description="Selected model")
    fallback_models: list[ModelDefinition] = Field(
        default_factory=list, description="Fallback models in order"
    )
    reasoning: str = Field(..., description="Why this model was selected")
    estimated_cost_usd: float = Field(..., description="Estimated cost for request")
    query_analysis: QueryAnalysis = Field(..., description="Query analysis results")


class ModelRouter:
    """
    Intelligent model router.
    
    Selects the optimal model based on:
    - Query complexity
    - Required capabilities
    - Cost optimization
    - Performance requirements
    - Compliance needs
    """
    
    def __init__(self) -> None:
        """Initialize the router."""
        self.registry = get_registry()
        self.analyzer = get_analyzer()
    
    def route(
        self,
        query: str,
        has_images: bool = False,
        has_audio: bool = False,
        force_model_id: Optional[str] = None,
        max_cost_usd: Optional[float] = None,
        compliance_domain: Optional[str] = None,
    ) -> RoutingDecision:
        """
        Route a query to the optimal model.
        
        Args:
            query: User's query text
            has_images: Whether images are attached
            has_audio: Whether audio is attached
            force_model_id: Force specific model (overrides routing)
            max_cost_usd: Maximum cost per request
            compliance_domain: Required compliance domain
            
        Returns:
            Routing decision with selected model and reasoning
            
        Raises:
            ModelNotFoundError: If no suitable model found
        """
        # If model is forced, use it
        if force_model_id:
            model = self.registry.get_model(force_model_id)
            return RoutingDecision(
                selected_model=model,
                fallback_models=[],
                reasoning="Model explicitly specified by user",
                estimated_cost_usd=0.0,  # Unknown without token count
                query_analysis=self.analyzer.analyze(query, has_images, has_audio),
            )
        
        # Analyze the query
        analysis = self.analyzer.analyze(query, has_images, has_audio)
        
        logger.info(
            "routing_query",
            complexity=analysis.complexity,
            modality=analysis.modality,
            intent=analysis.intent,
            reasoning_score=analysis.reasoning_score,
        )
        
        # Determine required model type based on modality
        required_type = self._determine_model_type(analysis)
        
        # Determine required capabilities
        required_capabilities = self._determine_capabilities(analysis)
        
        # Get candidate models
        candidates = self._get_candidate_models(
            model_type=required_type,
            required_capabilities=required_capabilities,
        )
        
        if not candidates:
            raise ModelNotFoundError(
                f"No models found for type={required_type}, capabilities={required_capabilities}"
            )
        
        # Select optimal model based on complexity and cost
        selected_model = self._select_optimal_model(
            candidates=candidates,
            analysis=analysis,
            max_cost_usd=max_cost_usd,
        )
        
        # Get fallback models (next 2 best options)
        fallback_models = [m for m in candidates if m.model_id != selected_model.model_id][:2]
        
        # Estimate cost (rough approximation)
        estimated_input_tokens = analysis.estimated_tokens
        estimated_output_tokens = self._estimate_output_tokens(analysis)
        estimated_cost = selected_model.calculate_cost(
            estimated_input_tokens, estimated_output_tokens
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(selected_model, analysis)
        
        decision = RoutingDecision(
            selected_model=selected_model,
            fallback_models=fallback_models,
            reasoning=reasoning,
            estimated_cost_usd=estimated_cost,
            query_analysis=analysis,
        )
        
        logger.info(
            "routing_decision_made",
            selected_model=selected_model.model_id,
            reasoning=reasoning,
            estimated_cost_usd=estimated_cost,
        )
        
        return decision
    
    def _determine_model_type(self, analysis: QueryAnalysis) -> ModelType:
        """Determine required model type from query analysis."""
        if analysis.modality == QueryModality.MULTIMODAL:
            return ModelType.MULTIMODAL
        elif analysis.modality == QueryModality.IMAGE:
            return ModelType.MULTIMODAL  # Need vision
        elif analysis.modality == QueryModality.AUDIO:
            return ModelType.AUDIO
        else:
            return ModelType.TEXT
    
    def _determine_capabilities(
        self, analysis: QueryAnalysis
    ) -> list[ModelCapability]:
        """Determine required capabilities from query analysis."""
        capabilities: list[ModelCapability] = []
        
        if analysis.requires_coding:
            capabilities.append(ModelCapability.CODING)
        
        if analysis.requires_reasoning:
            capabilities.append(ModelCapability.REASONING)
        
        if analysis.modality == QueryModality.IMAGE:
            capabilities.append(ModelCapability.VISION)
        
        if analysis.modality == QueryModality.AUDIO:
            capabilities.append(ModelCapability.AUDIO)
        
        return capabilities
    
    def _get_candidate_models(
        self,
        model_type: ModelType,
        required_capabilities: list[ModelCapability],
    ) -> list[ModelDefinition]:
        """Get candidate models that meet requirements."""
        # Get all active models of the required type
        candidates = self.registry.list_models(
            model_type=model_type,
            only_active=True,
        )
        
        # Filter by required capabilities
        if required_capabilities:
            candidates = [
                model
                for model in candidates
                if all(model.supports_capability(cap) for cap in required_capabilities)
            ]
        
        # Sort by cost (cheapest first)
        candidates.sort(
            key=lambda m: m.pricing.input_cost_per_1k_tokens
            + m.pricing.output_cost_per_1k_tokens
        )
        
        return candidates
    
    def _select_optimal_model(
        self,
        candidates: list[ModelDefinition],
        analysis: QueryAnalysis,
        max_cost_usd: Optional[float] = None,
    ) -> ModelDefinition:
        """
        Select the optimal model from candidates.
        
        Strategy:
        - SIMPLE queries → Cheapest model (e.g., GPT-3.5, Ollama)
        - MODERATE queries → Mid-tier model (e.g., Claude Sonnet, GPT-4)
        - COMPLEX queries → Best model (e.g., Claude Opus, GPT-4 Turbo)
        """
        if not candidates:
            raise ModelNotFoundError("No candidate models available")
        
        # For SIMPLE queries, use the cheapest model
        if analysis.complexity == QueryComplexity.SIMPLE:
            selected = candidates[0]  # Cheapest
            logger.debug("selected_cheapest_model", model_id=selected.model_id)
            return selected
        
        # For COMPLEX queries with high reasoning, use the best model
        if (
            analysis.complexity == QueryComplexity.COMPLEX
            or analysis.reasoning_score > 0.8
        ):
            # Find the most capable model (usually most expensive)
            selected = candidates[-1]  # Most expensive (usually best)
            logger.debug("selected_best_model", model_id=selected.model_id)
            return selected
        
        # For MODERATE queries, use mid-tier model
        # Try to find a balanced model (not cheapest, not most expensive)
        mid_index = len(candidates) // 2
        selected = candidates[mid_index] if mid_index > 0 else candidates[0]
        logger.debug("selected_mid_tier_model", model_id=selected.model_id)
        return selected
    
    def _estimate_output_tokens(self, analysis: QueryAnalysis) -> int:
        """Estimate output tokens based on query type."""
        if analysis.intent == QueryIntent.CONVERSATIONAL:
            return 50  # Short responses
        elif analysis.intent == QueryIntent.CREATIVE:
            return 500  # Longer creative content
        elif analysis.intent == QueryIntent.TECHNICAL:
            return 300  # Code + explanation
        elif analysis.complexity == QueryComplexity.COMPLEX:
            return 400  # Detailed explanation
        else:
            return 150  # Standard response
    
    def _generate_reasoning(
        self, model: ModelDefinition, analysis: QueryAnalysis
    ) -> str:
        """Generate human-readable reasoning for model selection."""
        reasons = []
        
        # Complexity-based reasoning
        if analysis.complexity == QueryComplexity.SIMPLE:
            reasons.append(
                f"Query is simple, using cost-effective model ({model.display_name})"
            )
        elif analysis.complexity == QueryComplexity.COMPLEX:
            reasons.append(
                f"Query is complex, using advanced model ({model.display_name})"
            )
        else:
            reasons.append(
                f"Query has moderate complexity, using balanced model ({model.display_name})"
            )
        
        # Capability-based reasoning
        if analysis.requires_coding:
            reasons.append("Selected for coding capability")
        
        if analysis.requires_reasoning:
            reasons.append(f"High reasoning score ({analysis.reasoning_score:.2f})")
        
        if analysis.modality != QueryModality.TEXT:
            reasons.append(f"Supports {analysis.modality} input")
        
        # Cost information
        cost_per_call = (
            model.pricing.input_cost_per_1k_tokens
            + model.pricing.output_cost_per_1k_tokens
        )
        reasons.append(f"Est. cost: ${cost_per_call:.4f} per 1K tokens")
        
        return "; ".join(reasons)


# Global router instance
_router: Optional[ModelRouter] = None


def get_router() -> ModelRouter:
    """
    Get the global model router instance.
    
    Returns:
        Model router singleton
    """
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
