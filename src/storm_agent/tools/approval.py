"""Approval tool for AI agents to request human approval."""

from .base import Tool
from ..utils.approval import ApprovalRequest, HumanApproval


class RequestApprovalTool(Tool):
    def __init__(self):
        super().__init__(
            name="request_approval",
            description="Request human approval before performing an operation",
            input_schema={
                "type": "object",
                "properties": {
                    "operation_description": {
                        "type": "string",
                        "description": "Clear description of what you want to do"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason why approval is needed"
                    }
                },
                "required": ["operation_description"]
            }
        )
        
    async def execute(self, operation_description: str, reason: str = None) -> str:
        """Request approval from human operator.
        
        Args:
            operation_description: Clear description of what you want to do
            reason: Optional reason why approval is needed
            
        Returns:
            Approval status and any feedback
        """
        full_description = operation_description
        if reason:
            full_description += f"\n\nReason: {reason}"
            
        request = ApprovalRequest(
            operation="model_requested_approval",
            description=full_description
        )
        
        approval = await HumanApproval.request(request)
        
        if approval.approved:
            return "APPROVED: You may proceed with the operation."
        else:
            return f"REJECTED: {approval.message or 'Operation not approved'}" 