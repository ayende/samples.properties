"""Utility functions for serialization"""
import json
from dataclasses import asdict, is_dataclass


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def dataclass_to_dict(obj, camel_case=False):
    """Convert a dataclass to a dictionary, optionally converting keys to camelCase"""
    if not is_dataclass(obj):
        return obj
    
    result = asdict(obj)
    if camel_case:
        result = {to_camel_case(k): v for k, v in result.items()}
    return result


def serialize_to_frontend(obj, camel_case=True):
    """Serialize an object or list of objects to a frontend-friendly format"""
    if obj is None:
        return None
    
    if isinstance(obj, list):
        return [serialize_to_frontend(item, camel_case) for item in obj]
    
    if is_dataclass(obj):
        data = asdict(obj)
        if camel_case:
            data = {to_camel_case(k): v for k, v in data.items()}
        return data
    
    if isinstance(obj, dict):
        if camel_case:
            return {to_camel_case(k) if isinstance(k, str) else k: serialize_to_frontend(v, camel_case) for k, v in obj.items()}
        return {k: serialize_to_frontend(v, camel_case) for k, v in obj.items()}
    
    return obj
