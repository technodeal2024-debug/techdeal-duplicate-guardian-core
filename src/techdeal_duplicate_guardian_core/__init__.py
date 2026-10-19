"""Local-only read-only duplicate file detection."""
from .scanner import DuplicateGroup, ScanReport, scan_duplicates
__all__ = ["DuplicateGroup", "ScanReport", "scan_duplicates"]
