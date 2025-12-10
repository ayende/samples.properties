"""Base class for all model entities"""


class EntityBase:
    """Base class providing identity-based hashing for all entities"""
    
    def __hash__(self):
        return hash(id(self))
    
    def __eq__(self, other):
        return self is other
