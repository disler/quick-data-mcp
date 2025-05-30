"""Dataset merging tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas


async def merge_datasets(
    dataset_configs: List[Dict[str, Any]], 
    join_strategy: str = "inner"
) -> dict:
    """Join datasets on common keys."""
    try:
        if len(dataset_configs) < 2:
            return {"error": "Need at least 2 datasets to merge"}
        
        # Start with first dataset
        first_config = dataset_configs[0]
        merged_df = DatasetManager.get_dataset(first_config["dataset_name"])
        
        merge_info = {
            "merge_strategy": join_strategy,
            "datasets_merged": [first_config["dataset_name"]],
            "final_shape": merged_df.shape,
            "merge_steps": []
        }
        
        # Merge with each subsequent dataset
        for config in dataset_configs[1:]:
            dataset_name = config["dataset_name"]
            join_column = config.get("join_column")
            
            df_to_merge = DatasetManager.get_dataset(dataset_name)
            
            if join_column:
                # Merge on specific column
                if join_column not in merged_df.columns:
                    return {"error": f"Join column '{join_column}' not found in merged dataset"}
                if join_column not in df_to_merge.columns:
                    return {"error": f"Join column '{join_column}' not found in dataset '{dataset_name}'"}
                
                before_shape = merged_df.shape
                merged_df = merged_df.merge(df_to_merge, on=join_column, how=join_strategy, suffixes=('', f'_{dataset_name}'))
                after_shape = merged_df.shape
                
                merge_info["merge_steps"].append({
                    "merged_with": dataset_name,
                    "join_column": join_column,
                    "before_shape": before_shape,
                    "after_shape": after_shape,
                    "rows_gained": after_shape[0] - before_shape[0],
                    "columns_gained": after_shape[1] - before_shape[1]
                })
            else:
                # Concatenate datasets
                before_shape = merged_df.shape
                merged_df = pd.concat([merged_df, df_to_merge], ignore_index=True, sort=False)
                after_shape = merged_df.shape
                
                merge_info["merge_steps"].append({
                    "concatenated_with": dataset_name,
                    "before_shape": before_shape,
                    "after_shape": after_shape,
                    "rows_added": after_shape[0] - before_shape[0]
                })
            
            merge_info["datasets_merged"].append(dataset_name)
        
        # Save merged dataset
        merged_name = f"merged_{'_'.join(merge_info['datasets_merged'])}"
        loaded_datasets[merged_name] = merged_df
        
        # Create schema for merged dataset
        from ..models.schemas import DatasetSchema
        schema = DatasetSchema.from_dataframe(merged_df, merged_name)
        dataset_schemas[merged_name] = schema
        
        merge_info.update({
            "merged_dataset_name": merged_name,
            "final_shape": merged_df.shape,
            "final_columns": list(merged_df.columns),
            "status": "success"
        })
        
        return merge_info
        
    except Exception as e:
        return {"error": f"Dataset merge failed: {str(e)}"}