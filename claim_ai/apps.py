from django.apps import AppConfig

MODULE_NAME = 'claim_ai'

DEFAULT_CONFIG = {
    'authentication': [],
    'ai_model_file': "",
    'claim_response_organization': 'openIMIS-Claim-AI',
    'date_format': '%Y-%m-%d',
}


class ClaimAiConfig(AppConfig):
    name = MODULE_NAME

    authentication = DEFAULT_CONFIG['authentication']
    ai_model_file = DEFAULT_CONFIG['ai_model_file']
    claim_response_organization = DEFAULT_CONFIG['claim_response_organization']
    date_format = DEFAULT_CONFIG['date_format']

    def _configure_perms(self, cfg):
        for config, config_value in cfg.items():
            setattr(ClaimAiConfig, config, config_value)

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CONFIG)
        self._configure_perms(cfg)
