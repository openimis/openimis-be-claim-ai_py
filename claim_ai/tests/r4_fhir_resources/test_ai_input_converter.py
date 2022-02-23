from django.test import testcases
import pandas
from pandas._testing import assert_frame_equal

from product.test_helpers import create_test_product

from claim_ai.evaluation.input_models.stored_input_model import ClaimBundleEvaluationAiInputModel
from claim_ai.rest_api.claim_evaluation.claim_bundle_evaluation_manager import ClaimBundleEvaluationManager
from core import datetime
from core.forms import User
from core.services import create_or_update_interactive_user, create_or_update_core_user

from insuree.test_helpers import create_test_insuree
from location.models import HealthFacility
from medical.test_helpers import create_test_item, create_test_service

from api_fhir_r4.tests import GenericTestMixin, LocationTestMixin
from api_fhir_r4.utils import TimeUtils, DbManagerUtils
from claim.models import Claim, ClaimItem, ClaimService
from medical.models import Diagnosis
from claim.test_helpers import create_test_claim_admin


class TestAiInputConverter(testcases.TestCase):
    _TEST_CODE = 'codeTest'
    _TEST_STATUS = Claim.STATUS_ENTERED
    _TEST_STATUS_DISPLAY = "entered"
    _TEST_OUTCOME = "queued"
    _TEST_ADJUSTMENT = "adjustment"
    _TEST_DATE_PROCESSED = "2010-11-16T00:00:00"
    _TEST_APPROVED = 1000.00
    _TEST_REJECTION_REASON = 0
    _TEST_VISIT_TYPE = "O"

    # claim item data
    _TEST_ITEM_CODE = "iCode"
    _TEST_ITEM_UUID = "AAAA76E2-DC28-4B48-8E29-3AC4ABEC0000"
    _TEST_ITEM_STATUS = Claim.STATUS_ENTERED
    _TEST_ITEM_QUANTITY = 20
    _TEST_ITEM_PRICE = 10.0
    _TEST_ITEM_REJECTED_REASON = 0

    # claim service data
    _TEST_SERVICE_CODE = "sCode"
    _TEST_SERVICE_UUID = "AAAA29BA-3F4E-4E6F-B55C-23A488A10000"
    _TEST_SERVICE_STATUS = Claim.STATUS_ENTERED
    _TEST_SERVICE_QUANTITY = 1
    _TEST_SERVICE_PRICE = 800
    _TEST_SERVICE_REJECTED_REASON = 0

    _TEST_ID = 9999
    _TEST_HISTORICAL_UUID = "AE580700-0277-4C98-ADAB-D98C0F700000"
    _TEST_HISTORICAL_ID = 9998
    _PRICE_ASKED_ITEM = 1000.0
    _PRICE_ASKED_SERVICE = 820.0
    _PRICE_APPROVED = 1000
    _ADMIN_AUDIT_USER_ID = -1

    _TEST_UUID = "AE580700-0277-4C98-ADAB-D98C0F7E681B"
    _TEST_ITEM_AVAILABILITY = True

    _TEST_ITEM_TYPE = 'D'
    _TEST_SERVICE_TYPE = 'D'

    # insuree and claim admin data
    _TEST_PATIENT_UUID = "76ACA309-F8CF-4890-8F2E-B416D78DE00B"
    _TEST_PATIENT_ID = 9283
    _TEST_CLAIM_ADMIN_UUID = "044C33D1-DBF3-4D6A-9924-3797B461E535"
    _TEST_CLAIM_ADMIN_ID = 9282

    _PRICE_VALUATED = 1000.0
    # hf test data
    _TEST_HF_ID = 10000
    _TEST_HF_UUID = "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F"
    _TEST_HF_CODE = "12345678"
    _TEST_HF_NAME = "TEST_NAME"
    _TEST_HF_LEVEL = "H"
    _TEST_HF_LEGAL_FORM = "G"
    _TEST_ADDRESS = "TEST_ADDRESS"
    _TEST_PHONE = "133-996-476"
    _TEST_FAX = "1-408-999 8888"
    _TEST_EMAIL = "TEST@TEST.com"

    _TEST_USER_NAME = "TestUserTest2"
    _TEST_USER_PASSWORD = "TestPasswordTest2"
    _TEST_DATA_USER = {
        "username": _TEST_USER_NAME,
        "last_name": _TEST_USER_NAME,
        "password": _TEST_USER_PASSWORD,
        "other_names": _TEST_USER_NAME,
        "user_types": "INTERACTIVE",
        "language": "en",
        "roles": [9],
    }

    _TEST_PRODUCT_CODE = "Test0004"

    def setUp(self):
        self._TEST_USER = self.get_or_create_user_api()
        self.item = create_test_item(
            self._TEST_ITEM_TYPE,
            custom_props={"code": self._TEST_ITEM_CODE, 'price': self._TEST_ITEM_PRICE}
        )
        self.item.uuid = self._TEST_ITEM_UUID
        self.item.save()
        self.service = create_test_service(
            self._TEST_SERVICE_TYPE,
            custom_props={"code": self._TEST_SERVICE_CODE, 'price': self._TEST_SERVICE_PRICE}
        )
        self.service.uuid = self._TEST_ITEM_UUID
        self.service.save()

        self._TEST_HF = self._create_test_health_facility()
        self._TEST_PRODUCT = self._create_test_product()

        self._EXPECTED_DATAFRAME = self._create_expected_df()

    def get_or_create_user_api(self):
        user = DbManagerUtils.get_object_or_none(User, username=self._TEST_USER_NAME)
        if user is None:
            user = self.__create_user_interactive_core()
        return user

    def __create_user_interactive_core(self):
        i_user, i_user_created = create_or_update_interactive_user(
            user_id=None, data=self._TEST_DATA_USER, audit_user_id=999, connected=False
        )
        create_or_update_core_user(
            user_uuid=None, username=self._TEST_DATA_USER["username"], i_user=i_user
        )
        return DbManagerUtils.get_object_or_none(User, username=self._TEST_USER_NAME)

    def test_dataframe_conversion(self):
        test_bundle_evaluation = self._create_test_idle_evaluation()
        actual_repr = ClaimBundleEvaluationAiInputModel(test_bundle_evaluation).to_representation()
        self._assert_df_repr(actual_repr)

    def _create_test_idle_evaluation(self):
        insuree = create_test_insuree()
        insuree.uuid = self._TEST_PATIENT_UUID
        insuree.id = self._TEST_PATIENT_ID
        insuree.save()
        historical_claim = self._create_test_claim(insuree, True)
        claim = self._create_test_claim(insuree)

        self._create_items_and_services(historical_claim, self._TEST_PRODUCT, self.item, self.service)
        item, service = self._create_items_and_services(claim, self._TEST_PRODUCT, self.item, self.service)
        claim_bundle_evaluation = ClaimBundleEvaluationManager(self._TEST_USER).create_idle_evaluation_bundle([claim])
        claim_bundle_evaluation = ClaimBundleEvaluationManager(self._TEST_USER).create_idle_evaluation_bundle([claim])
        return claim_bundle_evaluation

    def _create_items_and_services(self, claim, imis_product, item, service):
        claim_item = self._create_test_claim_item(claim, item, imis_product)
        claim_service = self._create_test_claim_service(claim, service, imis_product)
        return claim_item, claim_service

    def _create_test_claim_item(self, claim, provided, product):
        item = ClaimItem()
        item.item = provided
        item.product = product
        item.claim = claim
        item.status = self._TEST_ITEM_STATUS
        item.qty_approved = self._TEST_ITEM_QUANTITY
        item.qty_provided = self._TEST_ITEM_QUANTITY
        item.rejection_reason = self._TEST_ITEM_REJECTED_REASON
        item.availability = self._TEST_ITEM_AVAILABILITY
        item.price_asked = self._PRICE_ASKED_ITEM
        item.price_approved = self._TEST_ITEM_PRICE
        item.audit_user_id = self._ADMIN_AUDIT_USER_ID
        item.price_valuated = self._PRICE_VALUATED
        item.save()
        return item

    def _create_test_claim_service(self, claim, provided, product):
        service = ClaimService()
        service.service = provided
        service.product = product
        service.claim = claim
        service.status = self._TEST_SERVICE_STATUS
        service.qty_approved = self._TEST_SERVICE_QUANTITY
        service.qty_provided = self._TEST_SERVICE_QUANTITY
        service.rejection_reason = self._TEST_SERVICE_REJECTED_REASON
        service.availability = self._TEST_ITEM_AVAILABILITY
        service.price_asked = self._PRICE_ASKED_SERVICE
        service.price_approved = self._TEST_SERVICE_PRICE
        service.audit_user_id = self._ADMIN_AUDIT_USER_ID
        service.price_valuated = self._PRICE_VALUATED
        service.save()
        return service

    def _create_test_claim(self, insuree, historical=False):
        imis_claim = Claim()
        if not historical:
            imis_claim.id = self._TEST_ID
            imis_claim.uuid = self._TEST_UUID
        else:
            imis_claim.id = self._TEST_HISTORICAL_ID
            imis_claim.uuid = self._TEST_HISTORICAL_UUID
        imis_claim.code = self._TEST_CODE
        imis_claim.status = self._TEST_STATUS
        imis_claim.adjustment = self._TEST_ADJUSTMENT
        imis_claim.date_processed = TimeUtils.str_to_date(self._TEST_DATE_PROCESSED)
        imis_claim.approved = self._TEST_APPROVED
        imis_claim.rejection_reason = self._TEST_REJECTION_REASON
        imis_claim.insuree = insuree
        imis_claim.health_facility = self._TEST_HF

        if not historical:
            imis_claim.icd = Diagnosis(code='ICD00I')
            imis_claim.icd.audit_user_id = self._ADMIN_AUDIT_USER_ID
            imis_claim.icd.save()
        else:
            imis_claim.icd = Diagnosis(code='ICD00V')
            imis_claim.icd.audit_user_id = self._ADMIN_AUDIT_USER_ID
            imis_claim.icd.save()
        imis_claim.audit_user_id = self._ADMIN_AUDIT_USER_ID
        imis_claim.icd.date_from = datetime.date(2018, 12, 12)
        imis_claim.date_from = datetime.date(2018, 12, 12)
        imis_claim.date_claimed = datetime.date(2018, 12, 14)
        imis_claim.visit_type = self._TEST_VISIT_TYPE
        claim_admin = create_test_claim_admin()
        claim_admin.uuid = self._TEST_CLAIM_ADMIN_UUID
        claim_admin.id = self._TEST_CLAIM_ADMIN_ID
        claim_admin.health_facility = self._TEST_HF
        claim_admin.save()
        imis_claim.admin = claim_admin
        imis_claim.save()
        return imis_claim

    def _create_test_health_facility(self):
        location = LocationTestMixin().create_test_imis_instance()
        location.save()
        hf = HealthFacility()
        hf.id = self._TEST_HF_ID
        hf.uuid = self._TEST_HF_UUID
        hf.code = self._TEST_HF_CODE
        hf.name = self._TEST_HF_NAME
        hf.level = self._TEST_HF_LEVEL
        hf.legal_form_id = self._TEST_HF_LEGAL_FORM
        hf.address = self._TEST_ADDRESS
        hf.phone = self._TEST_PHONE
        hf.fax = self._TEST_FAX
        hf.email = self._TEST_EMAIL
        hf.location_id = location.id
        hf.offline = False
        hf.audit_user_id = -1
        hf.save()
        return hf

    def _assert_df_repr(self, actual_repr):
        claim_provisions = len(set(actual_repr.pop('ProvisionID')))
        self.assertEqual(claim_provisions, 4, "2 relevant and 2 historical unique items/services should be provided")
        assert_frame_equal(actual_repr, self._EXPECTED_DATAFRAME)

    def _create_expected_df(self):
        return pandas.DataFrame([
            {
                'ProvisionType': 'Medication',
                'ItemUUID': self.item.uuid,
                'HFUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'LocationId': self._TEST_HF.location.id,  # Is this HF location or insuree location?
                'ICDCode': 'ICD00I',
                'ICD1Code': None,
                'ProdID': self._TEST_PRODUCT.id,
                'DOB': datetime.date(1970, 1, 1),
                'Gender': 'M',  # Should it be code or  "Gender Object" used in ORM?
                'Poverty': None,
                'QuantityProvided': self._TEST_ITEM_QUANTITY,
                'ItemPrice': self._TEST_ITEM_PRICE,
                'PriceAsked': self._PRICE_ASKED_ITEM,
                'DateFrom': datetime.date(2018, 12, 12),
                'DateTo': datetime.date(2018, 12, 12),
                'DateClaimed': datetime.date(2018, 12, 14),
                'ItemFrequency': None,
                'ItemPatCat': 15,
                'ItemLevel': 'M',
                'HFLevel': 'H',
                'HFCareType': ' ',
                'VisitType': 'O',
                'RejectionReason': 0,
                'PriceValuated': self._PRICE_VALUATED,
                'HfUUID': self._TEST_HF.uuid,
                'ClaimAdminUUID': self._TEST_CLAIM_ADMIN_UUID,
                'InsureeUUID': self._TEST_PATIENT_UUID,
                'ClaimUUID': self._TEST_UUID,
                'New': 'new'
            }, {
                'ProvisionType': 'ActivityDefinition',
                'ItemUUID': self.service.uuid,
                'HFUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'LocationId': self._TEST_HF.location.id,
                'ICDCode': 'ICD00I',
                'ICD1Code': None,
                'ProdID': self._TEST_PRODUCT.id,
                'DOB': datetime.date(1970, 1, 1),
                'Gender': 'M',
                'Poverty': None,
                'QuantityProvided': self._TEST_SERVICE_QUANTITY,
                'ItemPrice': self._TEST_SERVICE_PRICE,
                'PriceAsked': self._PRICE_ASKED_SERVICE,
                'DateFrom': datetime.date(2018, 12, 12),
                'DateTo': datetime.date(2018, 12, 12),
                'DateClaimed': datetime.date(2018, 12, 14),
                'ItemFrequency': None,
                'ItemPatCat': 15,
                'ItemLevel': '1',
                'HFLevel': 'H',
                'HFCareType': ' ',
                'VisitType': 'O',
                'RejectionReason': 0,
                'PriceValuated': self._PRICE_VALUATED,
                'HfUUID': self._TEST_HF.uuid,
                'ClaimAdminUUID': self._TEST_CLAIM_ADMIN_UUID,
                'InsureeUUID': self._TEST_PATIENT_UUID,
                'ClaimUUID': self._TEST_UUID,
                'New': 'new'
            }, {
                'ProvisionType': 'Medication',
                'ItemUUID': self.item.uuid,
                'HFUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'LocationId': self._TEST_HF.location.id,
                'ICDCode': 'ICD00V',
                'ICD1Code': None,
                'ProdID': self._TEST_PRODUCT.id,
                'DOB': datetime.date(1970, 1, 1),
                'Gender': 'M',
                'Poverty': None,
                'QuantityProvided': self._TEST_ITEM_QUANTITY,
                'ItemPrice': self._TEST_ITEM_PRICE,
                'PriceAsked': self._PRICE_ASKED_ITEM,
                'DateFrom': datetime.date(2018, 12, 12),
                'DateTo': datetime.date(2018, 12, 12),
                'DateClaimed': datetime.date(2018, 12, 14),
                'ItemFrequency': None,
                'ItemPatCat': 15,
                'ItemLevel': 'M',
                'HFLevel': 'H',
                'HFCareType': ' ',
                'VisitType': 'O',
                'RejectionReason': 0,
                'PriceValuated': self._PRICE_VALUATED,
                'HfUUID': self._TEST_HF.uuid,
                'ClaimAdminUUID': self._TEST_CLAIM_ADMIN_UUID,
                'InsureeUUID': self._TEST_PATIENT_UUID,
                'ClaimUUID': self._TEST_HISTORICAL_UUID,
                'New': 'old'
            }, {
                'ProvisionType': 'ActivityDefinition',
                'ItemUUID': self.service.uuid,
                'HFUUID': "6D0EEA8C-62EB-11EA-94D6-C36229A16C2F",
                'LocationId': self._TEST_HF.location.id,
                'ICDCode': 'ICD00V',
                'ICD1Code': None,
                'ProdID': self._TEST_PRODUCT.id,
                'DOB': datetime.date(1970, 1, 1),
                'Gender': 'M',
                'Poverty': None,
                'QuantityProvided': self._TEST_SERVICE_QUANTITY,
                'ItemPrice': self._TEST_SERVICE_PRICE,
                'PriceAsked': self._PRICE_ASKED_SERVICE,
                'DateFrom': datetime.date(2018, 12, 12),
                'DateTo': datetime.date(2018, 12, 12),
                'DateClaimed': datetime.date(2018, 12, 14),
                'ItemFrequency': None,
                'ItemPatCat': 15,
                'ItemLevel': '1',
                'HFLevel': 'H',
                'HFCareType': ' ',
                'VisitType': 'O',
                'RejectionReason': 0,
                'PriceValuated': self._PRICE_VALUATED,
                'HfUUID': self._TEST_HF.uuid,
                'ClaimAdminUUID': self._TEST_CLAIM_ADMIN_UUID,
                'InsureeUUID': self._TEST_PATIENT_UUID,
                'ClaimUUID': self._TEST_HISTORICAL_UUID,
                'New': 'old'
            }
        ])

    def _create_test_product(self):
        imis_product = create_test_product(self._TEST_PRODUCT_CODE, valid=True, custom_props=None)
        imis_product.save()
        return imis_product
