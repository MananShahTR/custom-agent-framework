"""Simple human-in-the-loop approval system."""

from dataclasses import dataclass
from typing import Optional
from functools import wraps

@dataclass
class ApprovalRequest:
    operation: str
    description: str
    
@dataclass 
class ApprovalResponse:
    approved: bool
    message: str = ""

class HumanApproval:
    @staticmethod
    async def request(request: ApprovalRequest) -> ApprovalResponse:
        print(f"\n{'='*50}")
        print(f"🤖 APPROVAL REQUEST")
        print(f"{'='*50}")
        print(f"Operation: {request.operation}")
        print(f"Description: {request.description}")
        print(f"{'='*50}")
        
        while True:
            response = input("Approve this operation? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return ApprovalResponse(approved=True)
            elif response in ['n', 'no']:
                reason = input("Reason (optional): ")
                return ApprovalResponse(approved=False, message=reason)
            else:
                print("Please enter 'y' for yes or 'n' for no")

def require_approval(description: str):
    """Decorator to require human approval before executing a function."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = ApprovalRequest(
                operation=func.__name__,
                description=description
            )
            
            approval = await HumanApproval.request(request)
            
            if approval.approved:
                print(f"✅ Proceeding with {func.__name__}")
                return await func(*args, **kwargs)
            else:
                print(f"❌ Operation cancelled")
                return f"Operation cancelled: {approval.message}"
                
        return wrapper
    return decorator 