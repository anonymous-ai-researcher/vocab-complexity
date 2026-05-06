"""Load OWL ontologies and extract ALC interpretation structures."""

import os
import logging
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Interpretation:
    """An ALC interpretation I = (Delta^I, ·^I).

    Attributes:
        domain: Set of domain elements (individuals).
        concept_ext: Mapping from concept name A to A^I ⊆ Delta.
        role_ext: Mapping from role name r to r^I ⊆ Delta × Delta.
        sig_c: Tuple of concept names (Σ_C).
        sig_r: Tuple of role names (Σ_R).
    """

    domain: FrozenSet[str]
    concept_ext: Dict[str, FrozenSet[str]]
    role_ext: Dict[str, FrozenSet[Tuple[str, str]]]
    sig_c: Tuple[str, ...]
    sig_r: Tuple[str, ...]


@dataclass
class LabeledSample:
    """A labeled sample S = (I, P, N).

    Attributes:
        interpretation: The shared ALC interpretation.
        positives: Set of positive example individuals P ⊆ Delta^I.
        negatives: Set of negative example individuals N ⊆ Delta^I.
    """

    interpretation: Interpretation
    positives: FrozenSet[str]
    negatives: FrozenSet[str]

    @property
    def m(self) -> int:
        return len(self.positives) + len(self.negatives)


def load_ontology(owl_path: str) -> Interpretation:
    """Load an OWL ontology file and construct an ALC interpretation.

    Args:
        owl_path: Path to the .owl or .rdf file.

    Returns:
        An Interpretation instance.
    """
    try:
        from owlapy.owl_ontology_manager import OWLOntologyManager
    except ImportError:
        raise ImportError(
            "owlapy is required. Install with: pip install owlapy"
        )

    manager = OWLOntologyManager()
    ontology = manager.load_ontology(owl_path)

    individuals = frozenset(
        str(ind) for ind in ontology.individuals_in_signature()
    )
    concept_names = tuple(
        str(cls) for cls in ontology.classes_in_signature()
        if str(cls) != "http://www.w3.org/2002/07/owl#Thing"
    )
    role_names = tuple(
        str(prop) for prop in ontology.object_properties_in_signature()
    )

    concept_ext = {}
    for cls in ontology.classes_in_signature():
        cls_str = str(cls)
        if cls_str == "http://www.w3.org/2002/07/owl#Thing":
            continue
        instances = frozenset(
            str(ind) for ind in ontology.get_instances(cls)
        )
        concept_ext[cls_str] = instances

    role_ext = {}
    for prop in ontology.object_properties_in_signature():
        prop_str = str(prop)
        pairs = frozenset(
            (str(s), str(o))
            for s, o in ontology.get_object_property_values(prop)
        )
        role_ext[prop_str] = pairs

    interp = Interpretation(
        domain=individuals,
        concept_ext=concept_ext,
        role_ext=role_ext,
        sig_c=concept_names,
        sig_r=role_names,
    )
    logger.info(
        f"Loaded ontology: |Delta|={len(individuals)}, "
        f"|Sigma_C|={len(concept_names)}, |Sigma_R|={len(role_names)}"
    )
    return interp


def load_learning_problem(
    interpretation: Interpretation,
    lp_path: str,
) -> LabeledSample:
    """Load a learning problem (positive/negative example sets).

    Args:
        interpretation: The shared ALC interpretation.
        lp_path: Path to the learning problem file (JSON or OWL format).

    Returns:
        A LabeledSample instance.
    """
    import json

    with open(lp_path) as f:
        lp = json.load(f)

    positives = frozenset(lp["positives"])
    negatives = frozenset(lp["negatives"])

    assert positives <= interpretation.domain, "Positives not in domain"
    assert negatives <= interpretation.domain, "Negatives not in domain"
    assert not (positives & negatives), "Overlap between P and N"

    return LabeledSample(
        interpretation=interpretation,
        positives=positives,
        negatives=negatives,
    )


def get_stats(interp: Interpretation) -> dict:
    """Return ontology statistics for reporting."""
    return {
        "delta": len(interp.domain),
        "sig_c": len(interp.sig_c),
        "sig_r": len(interp.sig_r),
        "abox_size": sum(
            len(ext) for ext in interp.concept_ext.values()
        ) + sum(
            len(ext) for ext in interp.role_ext.values()
        ),
    }
