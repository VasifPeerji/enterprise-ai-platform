"""
📁 File: src/layer0_model_infra/registry.py
Layer: Layer 0 (Model Infrastructure)
Purpose: Central registry of all available models
Depends on: src/layer0_model_infra/models
Used by: Model router, gateway

The registry is the single source of truth for:
- Which models are available
- Model capabilities and pricing
- Compliance and performance characteristics
"""

from typing import Optional

from src.layer0_model_infra.models import (
    ComplianceDomain,
    ModelCapability,
    ModelDefinition,
    ModelLatency,
    ModelPricing,
    ModelProvider,
    ModelType,
)
from src.shared.errors import ModelNotFoundError
from src.shared.logger import get_logger

logger = get_logger(__name__)


class ModelRegistry:
    """
    Central registry for all models.
    
    This class maintains the catalog of available models and provides
    query methods for model selection.
    """
    
    def __init__(self) -> None:
        """Initialize the registry with default models."""
        self._models: dict[str, ModelDefinition] = {}
        self._initialize_default_models()
    
    def _initialize_default_models(self) -> None:
        """Initialize registry with commonly used models."""
        
        # ==========================================
        # OPENAI MODELS
        # ==========================================
        
        # GPT-4 Turbo
        self.register_model(
            ModelDefinition(
                model_id="gpt-4-turbo",
                model_name="gpt-4-turbo-preview",
                provider=ModelProvider.OPENAI,
                display_name="GPT-4 Turbo",
                description="Most capable GPT-4 model with 128k context",
                model_type=ModelType.TEXT,
                capabilities=[
                    ModelCapability.REASONING,
                    ModelCapability.CODING,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STREAMING,
                    ModelCapability.JSON_MODE,
                ],
                max_tokens=128000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_json_mode=True,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.01,
                    output_cost_per_1k_tokens=0.03,
                ),
                latency=ModelLatency(
                    p50_ms=2000,
                    p95_ms=5000,
                    p99_ms=8000,
                    time_to_first_token_ms=500,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
                is_recommended=True,
            )
        )
        
        # GPT-4 Vision
        self.register_model(
            ModelDefinition(
                model_id="gpt-4-vision",
                model_name="gpt-4-vision-preview",
                provider=ModelProvider.OPENAI,
                display_name="GPT-4 Vision",
                description="GPT-4 with vision capabilities",
                model_type=ModelType.MULTIMODAL,
                capabilities=[
                    ModelCapability.REASONING,
                    ModelCapability.VISION,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STREAMING,
                ],
                max_tokens=128000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_json_mode=False,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.01,
                    output_cost_per_1k_tokens=0.03,
                    image_cost=0.01,
                ),
                latency=ModelLatency(
                    p50_ms=3000,
                    p95_ms=7000,
                    p99_ms=10000,
                    time_to_first_token_ms=800,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
            )
        )
        
        # GPT-3.5 Turbo (cost-effective)
        self.register_model(
            ModelDefinition(
                model_id="gpt-3.5-turbo",
                model_name="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                display_name="GPT-3.5 Turbo",
                description="Fast and cost-effective model",
                model_type=ModelType.TEXT,
                capabilities=[
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STREAMING,
                    ModelCapability.JSON_MODE,
                ],
                max_tokens=16385,
                supports_streaming=True,
                supports_function_calling=True,
                supports_json_mode=True,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.0005,
                    output_cost_per_1k_tokens=0.0015,
                ),
                latency=ModelLatency(
                    p50_ms=800,
                    p95_ms=2000,
                    p99_ms=3000,
                    time_to_first_token_ms=200,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
            )
        )
        
        # ==========================================
        # ANTHROPIC MODELS
        # ==========================================
        
        # Claude Sonnet 4
        self.register_model(
            ModelDefinition(
                model_id="claude-sonnet-4",
                model_name="claude-sonnet-4-20250514",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude Sonnet 4",
                description="Anthropic's most balanced model",
                model_type=ModelType.TEXT,
                capabilities=[
                    ModelCapability.REASONING,
                    ModelCapability.CODING,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STREAMING,
                ],
                max_tokens=200000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_json_mode=False,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.003,
                    output_cost_per_1k_tokens=0.015,
                ),
                latency=ModelLatency(
                    p50_ms=1500,
                    p95_ms=4000,
                    p99_ms=6000,
                    time_to_first_token_ms=400,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
                is_recommended=True,
            )
        )
        
        # Claude Opus 4
        self.register_model(
            ModelDefinition(
                model_id="claude-opus-4",
                model_name="claude-opus-4-20250514",
                provider=ModelProvider.ANTHROPIC,
                display_name="Claude Opus 4",
                description="Anthropic's most capable model",
                model_type=ModelType.TEXT,
                capabilities=[
                    ModelCapability.REASONING,
                    ModelCapability.CODING,
                    ModelCapability.FUNCTION_CALLING,
                    ModelCapability.STREAMING,
                ],
                max_tokens=200000,
                supports_streaming=True,
                supports_function_calling=True,
                supports_json_mode=False,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.015,
                    output_cost_per_1k_tokens=0.075,
                ),
                latency=ModelLatency(
                    p50_ms=2500,
                    p95_ms=6000,
                    p99_ms=9000,
                    time_to_first_token_ms=600,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
            )
        )
        
        # ==========================================
        # EMBEDDING MODELS
        # ==========================================
        
        # OpenAI Embeddings
        self.register_model(
            ModelDefinition(
                model_id="text-embedding-3-small",
                model_name="text-embedding-3-small",
                provider=ModelProvider.OPENAI,
                display_name="OpenAI Embedding Small",
                description="Fast and cost-effective embeddings",
                model_type=ModelType.EMBEDDING,
                capabilities=[],
                max_tokens=8191,
                supports_streaming=False,
                supports_function_calling=False,
                supports_json_mode=False,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.00002,
                    output_cost_per_1k_tokens=0.0,
                ),
                latency=ModelLatency(
                    p50_ms=100,
                    p95_ms=300,
                    p99_ms=500,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
                is_recommended=True,
            )
        )
        
        self.register_model(
            ModelDefinition(
                model_id="text-embedding-3-large",
                model_name="text-embedding-3-large",
                provider=ModelProvider.OPENAI,
                display_name="OpenAI Embedding Large",
                description="High-quality embeddings for better retrieval",
                model_type=ModelType.EMBEDDING,
                capabilities=[],
                max_tokens=8191,
                supports_streaming=False,
                supports_function_calling=False,
                supports_json_mode=False,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.00013,
                    output_cost_per_1k_tokens=0.0,
                ),
                latency=ModelLatency(
                    p50_ms=150,
                    p95_ms=400,
                    p99_ms=600,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
            )
        )
        
        # ==========================================
        # OLLAMA MODELS (Local, Cost-Effective)
        # ==========================================
        
        # Llama 3.1 8B (Fast, local, free)
        self.register_model(
            ModelDefinition(
                model_id="ollama-llama3.1-8b",
                model_name="ollama/llama3.1:8b",
                provider=ModelProvider.LOCAL,
                display_name="Llama 3.1 8B (Ollama)",
                description="Fast local model, zero API costs",
                model_type=ModelType.TEXT,
                capabilities=[
                    ModelCapability.STREAMING,
                ],
                max_tokens=8192,
                supports_streaming=True,
                supports_function_calling=False,
                supports_json_mode=False,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.0,  # FREE - local
                    output_cost_per_1k_tokens=0.0,  # FREE - local
                ),
                latency=ModelLatency(
                    p50_ms=500,
                    p95_ms=1500,
                    p99_ms=3000,
                    time_to_first_token_ms=200,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
                is_recommended=True,  # Recommended for simple queries
            )
        )
        
        # Mistral 7B (Balanced local model)
        self.register_model(
            ModelDefinition(
                model_id="ollama-mistral-7b",
                model_name="ollama/mistral:7b",
                provider=ModelProvider.LOCAL,
                display_name="Mistral 7B (Ollama)",
                description="Balanced local model with good reasoning",
                model_type=ModelType.TEXT,
                capabilities=[
                    ModelCapability.REASONING,
                    ModelCapability.STREAMING,
                ],
                max_tokens=8192,
                supports_streaming=True,
                supports_function_calling=False,
                supports_json_mode=False,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.0,  # FREE - local
                    output_cost_per_1k_tokens=0.0,  # FREE - local
                ),
                latency=ModelLatency(
                    p50_ms=600,
                    p95_ms=1800,
                    p99_ms=3500,
                    time_to_first_token_ms=250,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
            )
        )
        
        # Phi-3 Mini (Ultra-fast local model)
        self.register_model(
            ModelDefinition(
                model_id="ollama-phi3-mini",
                model_name="ollama/phi3:mini",
                provider=ModelProvider.LOCAL,
                display_name="Phi-3 Mini (Ollama)",
                description="Ultra-fast local model for simple tasks",
                model_type=ModelType.TEXT,
                capabilities=[
                    ModelCapability.STREAMING,
                ],
                max_tokens=4096,
                supports_streaming=True,
                supports_function_calling=False,
                supports_json_mode=False,
                pricing=ModelPricing(
                    input_cost_per_1k_tokens=0.0,  # FREE - local
                    output_cost_per_1k_tokens=0.0,  # FREE - local
                ),
                latency=ModelLatency(
                    p50_ms=300,
                    p95_ms=800,
                    p99_ms=1500,
                    time_to_first_token_ms=100,
                ),
                compliance_domains=[ComplianceDomain.GENERAL],
                is_active=True,
                is_recommended=True,  # Recommended for very simple queries
            )
        )
        
        logger.info(
            "model_registry_initialized",
            total_models=len(self._models),
            providers=list(set(m.provider for m in self._models.values())),
        )
    
    def register_model(self, model: ModelDefinition) -> None:
        """
        Register a new model in the registry.
        
        Args:
            model: Model definition to register
        """
        self._models[model.model_id] = model
        logger.debug("model_registered", model_id=model.model_id, model_name=model.model_name)
    
    def get_model(self, model_id: str) -> ModelDefinition:
        """
        Get a model by its ID.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model definition
            
        Raises:
            ModelNotFoundError: If model not found in registry
        """
        if model_id not in self._models:
            raise ModelNotFoundError(model_id)
        
        model = self._models[model_id]
        
        if not model.is_active:
            logger.warning("inactive_model_requested", model_id=model_id)
        
        return model
    
    def get_model_by_name(self, model_name: str) -> ModelDefinition:
        """
        Get a model by its official name.
        
        Args:
            model_name: Official model name (e.g., 'gpt-4-turbo-preview')
            
        Returns:
            Model definition
            
        Raises:
            ModelNotFoundError: If model not found in registry
        """
        for model in self._models.values():
            if model.model_name == model_name:
                return model
        
        raise ModelNotFoundError(model_name)
    
    def list_models(
        self,
        model_type: Optional[ModelType] = None,
        provider: Optional[ModelProvider] = None,
        capability: Optional[ModelCapability] = None,
        compliance_domain: Optional[ComplianceDomain] = None,
        only_active: bool = True,
        only_recommended: bool = False,
    ) -> list[ModelDefinition]:
        """
        List models matching criteria.
        
        Args:
            model_type: Filter by model type
            provider: Filter by provider
            capability: Filter by capability
            compliance_domain: Filter by compliance domain
            only_active: Only return active models
            only_recommended: Only return recommended models
            
        Returns:
            List of matching models
        """
        models = list(self._models.values())
        
        # Apply filters
        if model_type:
            models = [m for m in models if m.model_type == model_type]
        
        if provider:
            models = [m for m in models if m.provider == provider]
        
        if capability:
            models = [m for m in models if m.supports_capability(capability)]
        
        if compliance_domain:
            models = [m for m in models if m.is_compliant_for(compliance_domain)]
        
        if only_active:
            models = [m for m in models if m.is_active]
        
        if only_recommended:
            models = [m for m in models if m.is_recommended]
        
        return models
    
    def get_recommended_model(
        self, model_type: ModelType = ModelType.TEXT
    ) -> ModelDefinition:
        """
        Get the recommended model for a given type.
        
        Args:
            model_type: Type of model needed
            
        Returns:
            Recommended model definition
            
        Raises:
            ModelNotFoundError: If no recommended model found
        """
        recommended = self.list_models(
            model_type=model_type,
            only_active=True,
            only_recommended=True,
        )
        
        if not recommended:
            raise ModelNotFoundError(
                f"No recommended model found for type: {model_type}"
            )
        
        return recommended[0]


# Global registry instance
_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    """
    Get the global model registry instance.
    
    Returns:
        Model registry singleton
    """
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
