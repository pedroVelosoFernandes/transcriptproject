import os
import uuid
from typing import Optional

from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

def get_memory_session_manager(session_id: Optional[str], actor_id: str,region: str,memory_id: str) -> Optional[AgentCoreMemorySessionManager]:
    if not memory_id:
        return None

    # AgentCoreMemoryConfig rejects None; OAuth/CUSTOM_JWT callers can reach us
    # without a runtime session header, so synthesize one when absent.
    session_id = session_id or uuid.uuid4().hex

    retrieval_config = {
        f"/assistant/{actor_id}/facts": RetrievalConfig(top_k=5, relevance_score=0.7),
        f"/assistant/{actor_id}/preferences": RetrievalConfig(top_k=5, relevance_score=0.7),
        f"/summaries/{actor_id}/{session_id}": RetrievalConfig(top_k=5, relevance_score=0.7),
    }

    return AgentCoreMemorySessionManager(
        AgentCoreMemoryConfig(
            memory_id=memory_id,
            session_id=session_id,
            actor_id=actor_id,
        ),
        region
    )

