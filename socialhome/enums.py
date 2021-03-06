from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class PolicyDocumentType(Enum):
    TERMS_OF_SERVICE = 'tos'
    PRIVACY_POLICY = 'privacypolicy'

    class Labels:
        TERMS_OF_SERVICE = _("Terms of service")
        PRIVACY_POLICY = _("Privacy policy")


class Visibility(Enum):
    PUBLIC = 0
    LIMITED = 1
    SITE = 2
    SELF = 3

    class Labels:
        PUBLIC = _("Public")
        LIMITED = _("Limited")
        SITE = _("Site")
        SELF = _("Self")
