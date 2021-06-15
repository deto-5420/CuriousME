from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import time
from binascii import unhexlify

from boto3 import Session
from django.db import models
from django.utils.encoding import force_text
from django_otp.models import Device
from django_otp.oath import TOTP
from django_otp.util import random_hex, hex_validator

from .conf import settings

logger = logging.getLogger(__name__)


def default_key():
    return force_text(random_hex(20))


def key_validator(value):
    return hex_validator(20)(value)


class AmazonSNSDevice(Device):
    """
    A :class:`~django_otp.models.Device` that delivers codes via the Amazon SNS
    service. This uses TOTP to generate temporary tokens, which are valid for
    :setting:`OTP_AMAZON_SNS_TOKEN_VALIDITY` seconds. Once a given token has been
    accepted, it is no longer valid, nor is any other token generated at an
    earlier time.
    .. attribute:: number
        *CharField*: The mobile phone number to deliver to (E.164).
    .. attribute:: key
        *CharField*: The secret key used to generate TOTP tokens.
    .. attribute:: last_t
        *BigIntegerField*: The t value of the latest verified token.
    """
    number = models.CharField(
        max_length=30,
        help_text="The mobile number to deliver tokens to (E.164)."
    )

    key = models.CharField(
        max_length=40,
        validators=[key_validator],
        default=default_key,
        help_text="A random key used to generate tokens (hex-encoded)."
    )

    last_t = models.BigIntegerField(
        default=-1,
        help_text="The t value of the latest verified token. The next token must be at a higher time step."
    )

    class Meta(Device.Meta):
        verbose_name = "Amazon SNS Device"

    @property
    def bin_key(self):
        return unhexlify(self.key.encode())

    def generate_challenge(self):
        """
        Sends the current TOTP token to ``self.number``.
        :returns: :setting:`OTP_AMAZON_SNS_CHALLENGE_MESSAGE` on success.
        :raises: Exception if delivery fails.
        """
        totp = self.totp_obj()
        token = format(totp.token(), '06d')

        if hasattr(self, 'OTP_AMAZON_SNS_TOKEN_TEMPLATE'):
            # This allows upstream to set the token template on a per device
            # basis. An use case for this could be allowing every user's
            # organization to customize messages
            tpl = self.OTP_AMAZON_SNS_TOKEN_TEMPLATE
        else:
            tpl = settings.OTP_AMAZON_SNS_TOKEN_TEMPLATE

        message = tpl.format(token=token)
        if settings.OTP_AMAZON_SNS_NO_DELIVERY:
            logger.info(message)
        else:
            self._deliver_token(message)

        challenge = settings.OTP_AMAZON_SNS_CHALLENGE_MESSAGE.format(token=token)

        return challenge

    def _deliver_token(self, token):
        client = Session().client('sns')
        try:
            client.publish(
                PhoneNumber=self.number,
                Message=str(token)
            )
        except Exception as e:
            logger.exception('Error sending token by Amazon SNS: {0}'.format(e))
            raise

    def verify_token(self, token):
        try:
            token = int(token)
        except Exception:
            verified = False
        else:
            totp = self.totp_obj()
            tolerance = settings.OTP_AMAZON_SNS_TOKEN_VALIDITY

            for offset in range(-tolerance, 1):
                totp.drift = offset
                if (totp.t() > self.last_t) and (totp.token() == token):
                    self.last_t = totp.t()
                    self.save()

                    verified = True
                    break
            else:
                verified = False

        return verified

    def totp_obj(self):
        totp = TOTP(self.bin_key, step=1)
        totp.time = time.time()

        return totp