from django.apps import AppConfig

MODULE_NAME = 'claim_ai'

DEFAULT_CONFIG = {
    'authentication': [],
    'ai_model_file': "",
    'claim_response_organization': 'openIMIS-Claim-AI'
}

DEFAULT_CATEGORICAL_VARIABLES_MAPPING = {
    'link.type': {
        'Brother/Sister': 1,
        'Father/Mother': 2,
        'Uncle/Aunt': 3,
        'Son/Daughter': 4,
        'Grand parents': 5,
        'Employee': 6,
        'Others': 7,
        'Spouse': 8,
    }
}


class ClaimAiConfig(AppConfig):
    name = MODULE_NAME

    authentication = DEFAULT_CONFIG['authentication']
    ai_model_file = DEFAULT_CONFIG['ai_model_file']
    claim_response_organization = DEFAULT_CONFIG['claim_response_organization']
    link_type_categorical_mapping = DEFAULT_CATEGORICAL_VARIABLES_MAPPING['link.type']

    def _configure_perms(self, cfg):
        for config, config_value in cfg.items():
            setattr(ClaimAiConfig, config, config_value)

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CONFIG)
        self._configure_perms(cfg)