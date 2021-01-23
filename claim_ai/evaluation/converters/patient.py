from claim_ai.evaluation import input_models
from claim_ai.evaluation.converters.base_converter import AbstractConverter


class PatientConverter(AbstractConverter):

    def to_ai_input(self, claim):
        claim_patient = claim['patient']
        contained_patient = next(contained for contained in claim['contained']
                                 if contained['resourceType'] == 'Patient')

        patient = input_models.Patient(
            identifier=self._get_claim_patient_identifier(claim_patient),
            birth_date=self._get_contained_patient_birth_date(contained_patient),
            gender=self._get_contained_patient_gender(contained_patient),
            is_head=self._get_contained_patient_is_head(contained_patient),
            link_type=self._get_contained_patient_link_type(contained_patient),
            poverty_status=self._get_contained_patient_poverty_status(contained_patient),
            location_code=self._get_contained_patient_location_code(contained_patient),
            group=self._get_contained_patient_group(contained_patient),
        )
        return patient

    def _get_claim_patient_identifier(self, claim_patient):
        return claim_patient['identifier']['value']

    def _get_contained_patient_birth_date(self, contained_patient):
        return contained_patient['birthDate']

    def _get_contained_patient_gender(self, contained_patient):
        return contained_patient['gender']

    def _get_contained_patient_is_head(self, contained_patient):
        # IMIS value for isHead extension url: https://openimis.atlassian.net/wiki/spaces/OP/pages/960069653/isHead"
        return next(extension['valueBoolean'] for extension in contained_patient['extension']
                    if extension['url'].endswith('isHead'))

    def _get_contained_patient_link_type(self, contained_patient):
        # TODO: What should be this value
        return contained_patient['identifier'][0]['type']['coding'][0]['code']

    def _get_contained_patient_poverty_status(self, contained_patient):
        # PovertyStatus is optional extension, False is returned if not found
        return next((extension['value'] for extension in contained_patient['extension']
                    if extension['url'].endswith('povertyStatus')) or [], False)

    def _get_contained_patient_location_code(self, contained_patient):
        location_extension = next(extension for extension in contained_patient['extension']
                                  if extension['url'].endswith('locationCode'))
        return location_extension['valueReference']['identifier']['value']

    def _get_contained_patient_group(self, contained_patient):
        # TODO: This extension is not yet available in fhir api, returns None as default
        return next((extension['value'] for extension in contained_patient['extension']
                     if extension['url'].endswith('povertyStatus')) or [], None)
