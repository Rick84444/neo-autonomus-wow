from dataclasses import dataclass

@dataclass
class AgentPolicy:
    cost_cap_tokens: int = 150000
    time_cap_s: int = 600
    regulated_control: bool = True
    require_dual_confirm_finance: bool = True
    allowed_finance_apis: tuple = ("bank_demo","broker_demo")

POLICY = AgentPolicy()
