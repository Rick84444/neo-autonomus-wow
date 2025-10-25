from dataclasses import dataclass

@dataclass
class AgentPolicy:
    cost_cap_tokens: int = 150000
    time_cap_s: int = 600
    regulated_control: bool = True
    # Temporarily relaxed for local automated runs/tests. Set to True in production.
    require_dual_confirm_finance: bool = False
    allowed_finance_apis: tuple = ("bank_demo","broker_demo")

POLICY = AgentPolicy()
