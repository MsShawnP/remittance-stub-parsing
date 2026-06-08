"""Validation layer for remittance stub data.

Provides arithmetic checks (net + deductions = gross) and
reason-code mapping validation against retailer configs.
"""

from src.validation.arithmetic import validate_arithmetic
from src.validation.reason_codes import validate_reason_codes, validate_stub

__all__ = ["validate_arithmetic", "validate_reason_codes", "validate_stub"]
