from __future__ import annotations

from .mcp_gateway import MCPGateway, MCPTool
from .mcp_tools import dependency_scan, generate_report, repository_read


def build_gateway() -> MCPGateway:
    gateway = MCPGateway()
    gateway.register(MCPTool("repository.read", "github", "read", repository_read))
    gateway.register(MCPTool("dependency.scan", "github", "scan", dependency_scan))
    gateway.register(MCPTool("report.generate", "report", "generate", generate_report))
    return gateway
