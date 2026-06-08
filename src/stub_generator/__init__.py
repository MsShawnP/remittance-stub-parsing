"""Synthetic remittance stub generators for four retailer formats."""

from pathlib import Path

from .costco import CostcoStubGenerator
from .keHE import KeheStubGenerator
from .unfi import UnfiStubGenerator
from .walmart import WalmartStubGenerator


def generate_all_stubs(output_dir: Path) -> list[Path]:
    """Run all four retailer generators and return all output file paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    all_paths = []

    generators = [
        WalmartStubGenerator(),
        CostcoStubGenerator(),
        UnfiStubGenerator(),
        KeheStubGenerator(),
    ]

    for generator in generators:
        paths = generator.generate(output_dir)
        all_paths.extend(paths)

    return all_paths
