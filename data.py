# data.py -> Data loading and MGMNT module

import os
import pandas as pd
import logging
from functools import lru_cache
from fastapi import HTTPException
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("capstone_data")

@lru_cache(maxsize=1)
def load_csv() -> pd.DataFrame:
    """Load and cache csv data with extended documentation."""

    try:
        df = pd.DataFrame({
            "id": [1,2,3,4,5,6,7],
            "text": [
                "Generative AI creates realistic synthetic images.",
                "LLMs enable human-like conversational experiences.",
                "AI models can generate code from natural language.",
                "Text-to-image systems turn prompts into art.",
                "Generative AI powers personalized content creation.",
                "AI can summarize complex documents instantly.",
                "Generative models accelerate drug discovery pipelines."
            ]
        })
        logger.info(f"Loaded CSV with {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV: {str(e)}")
        raise HTTPException(status_code=500, detail="Error loading data.")
    
def get_data_summary()-> dict:
    """Get summary statistics about the data"""
    df = load_csv()
    return {
        "total_records": len(df),
        "columns": list(df.columns),
        "data_types": df.dtypes.to_dict()
    }