from app.schemas.common import APIModel


class MCPTool(APIModel):
    name: str
    description: str
    method: str
    path: str
    requires_wallet: bool = True
    enabled: bool = True


class MCPManifestResponse(APIModel):
    version: str
    tools: list[MCPTool]
