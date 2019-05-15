# -*- coding: utf-8 -*-
import warnings
import base64

import django
# import six
from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

try:
    import hvac
except ImportError:
    raise ImportError('Using an encrypted field requires the hvac module. '
                      'You can obtain hvac from https://hvac.readthedocs.io/.')


class EncryptionWarning(RuntimeWarning):
    pass


class BaseEncryptedField(models.Field):
    prefix = 'vault'

    def __init__(self, *args, **kwargs):
        # if not getattr(settings, 'ENCRYPTED_FIELD_KEYS_DIR', None):
        #     raise ImproperlyConfigured('You must set the settings.ENCRYPTED_FIELD_KEYS_DIR '
        #                                'setting to your Keyczar keys directory.')
        # crypt_class = self.get_crypt_class()
        # self.crypt = crypt_class.Read(settings.ENCRYPTED_FIELD_KEYS_DIR)
        vault_url = getattr(settings, 'VAULT_URL', None)
        vault_token = getattr(settings, 'VAULT_TOKEN', None)
        vault_transit_key = getattr(settings, 'VAULT_TRANSIT', None)

        if not vault_url:
            raise ImproperlyConfigured('You must set the settings.VAULT_URL')

        if not vault_token:
            raise ImproperlyConfigured('You must set the settings.VAULT_TOKEN')

        if not vault_transit_key:
            raise ImproperlyConfigured('You must set the settings.VAULT_TRANSIT_KEY')
        
        self.client = hvac.Client(
            url=vault_url,
            token=vault_token
        )
        

        # Encrypted size is larger than unencrypted
        self.unencrypted_length = max_length = kwargs.get('max_length', None)
        if max_length:
            kwargs['max_length'] = self.calculate_crypt_max_length(max_length)

        super(BaseEncryptedField, self).__init__(*args, **kwargs)

    def calculate_crypt_max_length(self, unencrypted_length):
        # TODO: Re-examine if this logic will actually make a large-enough
        # max-length for unicode strings that have non-ascii characters in them.
        # For PostGreSQL we might as well always use textfield since there is little
        # difference (except for length checking) between varchar and text in PG.
        return len(self.prefix) + len(self.crypt.Encrypt('x' * unencrypted_length))

    # def get_crypt_class(self):
    #     """
    #     Get the Keyczar class to use.
    #     The class can be customized with the ENCRYPTED_FIELD_MODE setting. By default,
    #     this setting is DECRYPT_AND_ENCRYPT. Set this to ENCRYPT to disable decryption.
    #     This is necessary if you are only providing public keys to Keyczar.
    #     Returns:
    #         keyczar.Encrypter if ENCRYPTED_FIELD_MODE is ENCRYPT.
    #         keyczar.Crypter if ENCRYPTED_FIELD_MODE is DECRYPT_AND_ENCRYPT.
    #     Override this method to customize the type of Keyczar class returned.
    #     """
    #     crypt_type = getattr(settings, 'ENCRYPTED_FIELD_MODE', 'DECRYPT_AND_ENCRYPT')
    #     if crypt_type == 'ENCRYPT':
    #         crypt_class_name = 'Encrypter'
    #     elif crypt_type == 'DECRYPT_AND_ENCRYPT':
    #         crypt_class_name = 'Crypter'
    #     else:
    #         raise ImproperlyConfigured(
    #             'ENCRYPTED_FIELD_MODE must be either DECRYPT_AND_ENCRYPT '
    #             'or ENCRYPT, not %s.' % crypt_type)
    #     return getattr(keyczar, crypt_class_name)

    def to_python(self, value):
        """
        Descript value from DB is encrypted
        """
        if isinstance(self.crypt.primary_key, keyczar.keys.RsaPublicKey):
            retval = value
        elif value and (value.startswith(self.prefix)):
            if hasattr(self.crypt, 'Decrypt'):
                retval = self.crypt.Decrypt(value[len(self.prefix):])
                if six.PY2 and retval:
                    retval = retval.decode('utf-8')
            else:
                retval = value
        else:
            retval = value
        return retval

    # if django.VERSION < (2, ):
    #     def from_db_value(self, value, expression, connection, context):
    #         return self.to_python(value)
    # else:
    def from_db_value(self, value, expression, connection):  # type: ignore
        return self.to_python(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if value and not value.startswith(self.prefix):
            # We need to encode to base64 first, Vault transit 
            # expects a base64 encoded string
            plaintext = base64.urlsafe_b64encode(value).decode('ascii')

            # Truncated encrypted content is unreadable,
            # so truncate before encryption
            max_length = self.unencrypted_length
            if max_length and len(plaintext) > max_length:
                warnings.warn("Truncating field %s from %d to %d bytes" % (
                    self.name, len(plaintext), max_length), EncryptionWarning
                )
                plaintext = plaintext[:max_length]

            encrypt_data_response = self.client.secrets.transit.encrypt_data(
                    name=self.vault_transit_key,
                    plaintext=base64.urlsafe_b64encode('hi its me hvac').decode('ascii'),
            )
            ciphertext = encrypt_data_response['data']['ciphertext']

        # if value and not value.startswith(self.prefix):
        #     # We need to encode a unicode string into a byte string, first.
        #     # keyczar expects a bytestring, not a unicode string.
        #     if six.PY2:
        #         if type(value) == six.types.UnicodeType:
        #             value = value.encode('utf-8')
        #     # Truncated encrypted content is unreadable,
        #     # so truncate before encryption
        #     max_length = self.unencrypted_length
        #     if max_length and len(value) > max_length:
        #         warnings.warn("Truncating field %s from %d to %d bytes" % (
        #             self.name, len(value), max_length), EncryptionWarning
        #         )
        #         value = value[:max_length]

        #     value = self.prefix + self.crypt.Encrypt(value)
        # return value

    def deconstruct(self):
        name, path, args, kwargs = super(BaseEncryptedField, self).deconstruct()
        kwargs['max_length'] = self.unencrypted_length
        return name, path, args, kwargs


class EncryptedTextField(BaseEncryptedField):
    def get_internal_type(self):
        return 'TextField'

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(EncryptedTextField, self).formfield(**defaults)


class EncryptedCharField(BaseEncryptedField):
    def __init__(self, *args, **kwargs):
        super(EncryptedCharField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(EncryptedCharField, self).formfield(**defaults)