from functools import lru_cache

from fhir.resources.bundle import Bundle

from api_fhir_r4.configurations import R4IdentifierConfig
from api_fhir_r4.converters import BaseFHIRConverter
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders import ClaimResponseBuilderFactory
from claim_ai.evaluation.converters.r4_fhir_resources.fhir_response_builders.base_builders.bundle_builders import \
    ClaimBundleEvaluationClaimResponseBundleBuilder
from claim_ai.models import ClaimBundleEvaluation, SingleClaimEvaluationResult


class ResponseHandler:
    def to_representation(self, obj):
        representation_handlers = self._get_handlers()
        handler = representation_handlers.get(obj.__class__)
        if handler:
            return handler(obj)
        else:
            raise NotImplementedError(
                f"Can't create representation for object of type: {obj.__class__}, "
                f"allowed types are: {representation_handlers.keys()}")

    @lru_cache(maxsize=None)
    def _get_handlers(self):
        return {
            Bundle: lambda obj: obj.dict(),
            ClaimBundleEvaluation: lambda obj: self._build_bundle_response(obj),
            SingleClaimEvaluationResult: lambda obj: self._build_claim_response(obj)
        }

    def _build_bundle_response(self, obj):
        converter = ClaimBundleEvaluationClaimResponseBundleBuilder(ClaimResponseBuilderFactory())
        response = converter.build_fhir_bundle(obj, None)
        response.identifier = self.__build_bundle_identifier(obj)
        return response.dict()

    def _build_claim_response(self, obj):
        converter = ClaimResponseBuilderFactory().get_builder(SingleClaimEvaluationResult.__name__)
        return converter.build_valid_claim_response(obj, obj.evaluated_items.all()).dict()

    def __build_bundle_identifier(self, evaluation_info):
        return BaseFHIRConverter.build_fhir_identifier(
            evaluation_info.evaluation_hash,
            R4IdentifierConfig.get_fhir_identifier_type_system(),
            R4IdentifierConfig.get_fhir_uuid_type_code()
        )


class RequestToInternalValueHandler:
    def __init__(self, claim_converter, audit_user_id):
        self.converter = claim_converter
        self.audit_user_id = audit_user_id

    def to_internal_value(self, data):
        if data['resourceType'] == 'Bundle':
            return {'claims': self._claims_from_bundle(data), 'bundle_id': self._get_bundle_id(data)}
        elif data['resourceType'] == 'Claim':
            return {'claims': [self._create_claim_from_entry(data)], 'bundle_id': self._get_clam_id(data)}

    def _claims_from_bundle(self, bundle):
        out = []
        for next_entry in bundle['entry']:
            out.append(self._create_claim_from_entry(next_entry['resource']))
        return out

    def _create_claim_from_entry(self, next_entry):
        # Transform to imis using default converter and parse to dict.
        resource = next_entry
        imis_claim = self.converter.to_imis_obj(resource, self.audit_user_id).__dict__
        if resource.get('id', None):
            imis_claim['uuid'] = resource['id']
        return imis_claim

    def _get_bundle_id(self, data):
        if data.get('identifier', None):
            return data['identifier']['value']

    def _get_clam_id(self, data):
        if data.get('id', None):
            return data['id']
