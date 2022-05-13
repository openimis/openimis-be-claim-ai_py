from dataclasses import dataclass

from fhir.resources.resource import Resource


@dataclass
class FhirClaimInformation:
    fhir_resource: Resource
    claim_resource: dict
