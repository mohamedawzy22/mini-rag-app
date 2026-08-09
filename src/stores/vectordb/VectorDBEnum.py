from enum import Emum

class VectorDBEnum(Emum):
    
    QDRANT = "QDRANT"
    
class DistanceMethodEnums(Emum):
    COSINE = "cosine"
    DOT = "dot"