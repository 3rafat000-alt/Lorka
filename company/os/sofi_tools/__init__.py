"""
sofi_tools — SOFI AI shared agent library ("desks").

Stdlib-first toolkit every agent imports to do its job against the company brain:
read/write project state, chain handoff tickets, resolve routes, validate gates,
and stay inside the governance sandbox.

Law: engine/tooling/GOVERNANCE.md. Discovery index: engine/tooling/registry.yaml.
Nothing here reaches outside the repo or a project's own directory.
"""
__version__ = "1.0.0"

from . import paths, brain, tickets, routing, gates, guard, runlog  # noqa: F401

__all__ = ["paths", "brain", "tickets", "routing", "gates", "guard", "runlog"]
