"""
Configurable validation rules endpoints.
"""
from fastapi import APIRouter, Depends, Body, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from src.db.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ValidationRule(BaseModel):
    """Validation rule configuration."""
    rule_name: str = Field(..., description="Name of the validation rule")
    rule_type: str = Field(..., description="Type: missing_threshold, range_check, format_check, etc.")
    enabled: bool = Field(True, description="Whether the rule is enabled")
    parameters: Dict = Field(default_factory=dict, description="Rule-specific parameters")


class ValidationConfig(BaseModel):
    """Complete validation configuration."""
    config_name: str = Field(..., description="Configuration name")
    rules: List[ValidationRule] = Field(..., description="List of validation rules")
    description: Optional[str] = Field(None, description="Configuration description")


# In-memory storage for validation configurations (use database in production)
validation_configs: Dict[str, ValidationConfig] = {}


@router.post("/config/validation-rules", tags=["Configuration"])
async def create_validation_config(config: ValidationConfig) -> Dict:
    """
    Create a new validation configuration with custom rules.
    
    Example config:
    {
        "config_name": "strict_validation",
        "description": "Strict validation rules",
        "rules": [
            {
                "rule_name": "no_missing_values",
                "rule_type": "missing_threshold",
                "enabled": True,
                "parameters": {"threshold": 0}
            },
            {
                "rule_name": "age_range",
                "rule_type": "range_check",
                "enabled": True,
                "parameters": {"column": "age", "min": 0, "max": 120}
            }
        ]
    }
    """
    validation_configs[config.config_name] = config
    
    return {
        "message": f"Validation configuration '{config.config_name}' created successfully",
        "config_name": config.config_name,
        "rules_count": len(config.rules)
    }


@router.get("/config/validation-rules", tags=["Configuration"])
async def list_validation_configs() -> Dict:
    """
    List all available validation configurations.
    """
    return {
        "configs": [
            {
                "config_name": name,
                "rules_count": len(config.rules),
                "description": config.description
            }
            for name, config in validation_configs.items()
        ]
    }


@router.get("/config/validation-rules/{config_name}", tags=["Configuration"])
async def get_validation_config(config_name: str) -> ValidationConfig:
    """
    Get a specific validation configuration.
    """
    if config_name not in validation_configs:
        raise HTTPException(status_code=404, detail=f"Configuration '{config_name}' not found")
    
    return validation_configs[config_name]


@router.put("/config/validation-rules/{config_name}", tags=["Configuration"])
async def update_validation_config(config_name: str, config: ValidationConfig) -> Dict:
    """
    Update an existing validation configuration.
    """
    if config_name not in validation_configs:
        raise HTTPException(status_code=404, detail=f"Configuration '{config_name}' not found")
    
    validation_configs[config_name] = config
    
    return {
        "message": f"Validation configuration '{config_name}' updated successfully",
        "config_name": config.config_name
    }


@router.delete("/config/validation-rules/{config_name}", tags=["Configuration"])
async def delete_validation_config(config_name: str) -> Dict:
    """
    Delete a validation configuration.
    """
    if config_name not in validation_configs:
        raise HTTPException(status_code=404, detail=f"Configuration '{config_name}' not found")
    
    del validation_configs[config_name]
    
    return {
        "message": f"Validation configuration '{config_name}' deleted successfully"
    }

