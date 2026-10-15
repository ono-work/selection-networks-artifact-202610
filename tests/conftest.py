"""Test-collection configuration for the public artifact.

Two tests in tests/test_v49_d6_closure_audit.py call
``src.v49_d6_closure_audit.build_certificate()``, which -- by design of the
original audit tool -- REGENERATES
``experiments/v49_d6_closure_audit/coverage_certificate.json`` in place
(with absolute artifact paths of the machine it runs on). The as-published
certificate is preserved byte-for-byte in the frozen bundle
``experiments/v49_d6_final/bundle/experiments/v49_d6_closure_audit/`` and is
hash-pinned by ``evidence_manifest.json``, so regenerating the live copy is
a supported reproduction step; it is skipped by default only so that a plain
``pytest`` run leaves every copied evidence file untouched.

Set ``ARTIFACT_ALLOW_CERT_REBUILD=1`` to run those tests (this rewrites the
live certificate; afterwards ``scripts/check_v49_references.py`` will report
it as a divergence from the bundle, which is expected).
"""
import os

import pytest

MUTATING_TESTS = {
    "test_closure_certificate_passes_and_has_expected_open_residuals",
    "test_non_residual_classifications_have_provenance_or_explicit_a5_dependency",
}


def pytest_collection_modifyitems(config, items):
    if os.environ.get("ARTIFACT_ALLOW_CERT_REBUILD") == "1":
        return
    skip = pytest.mark.skip(
        reason="regenerates experiments/v49_d6_closure_audit/"
               "coverage_certificate.json in place; set "
               "ARTIFACT_ALLOW_CERT_REBUILD=1 to run (see tests/conftest.py)")
    for item in items:
        if item.name in MUTATING_TESTS:
            item.add_marker(skip)
