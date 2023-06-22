# -*- coding: utf-8 -*-
import warnings
import datetime
import base64
import os

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

    def __init__(self, data_type="string", *args, **kwargs):
        # if not getattr(settings, 'ENCRYPTED_FIELD_KEYS_DIR', None):
        #     raise ImproperlyConfigured('You must set the settings.ENCRYPTED_FIELD_KEYS_DIR '
        #                                'setting to your Keyczar keys directory.')
        # crypt_class = self.get_crypt_class()
        # self.crypt = crypt_class.Read(settings.ENCRYPTED_FIELD_KEYS_DIR)
        self.running_as_test = False
        if 'GITHUB_WORKFLOW' in os.environ or getattr(settings, 'TESTING', False):
            self.running_as_test = True

        vault_url = getattr(settings, 'VAULT_ADDR', None)
        vault_token = getattr(settings, 'VAULT_TOKEN', None)
        self.vault_transit_key = getattr(settings, 'VAULT_TRANSIT_KEY', None)

        if not vault_url:
            raise ImproperlyConfigured('You must set the settings.VAULT_ADDR')

        if not vault_token:
            raise ImproperlyConfigured('You must set the settings.VAULT_TOKEN')

        if not self.vault_transit_key:
            raise ImproperlyConfigured('You must set the settings.VAULT_TRANSIT_KEY')
        
        self.client = hvac.Client(
            url=vault_url,
            token=vault_token
        )

        # # Encrypted size is larger than unencrypted
        # self.unencrypted_length = max_length = kwargs.get('max_length', None)
        # if max_length:
        #     kwargs['max_length'] = self.calculate_crypt_max_length(max_length)
        self.data_type = data_type

        super(BaseEncryptedField, self).__init__(*args, **kwargs)

    # def calculate_crypt_max_length(self, unencrypted_length):
    #     # max-length for unicode strings that have non-ascii characters in them.
    #     # UTF-8 Characters can use 1 - 4 bytes for a character. 
    #     # In general a textfield might be preferrable, as the encrypted value can be 
    #     # much longer then the plain text. 
    #     # For PostGreSQL we might as well always use textfield since there is little
    #     # difference (except for length checking) between varchar and text in PG.
        
    #     # return len(self.prefix) + len(self.crypt.Encrypt('x' * unencrypted_length))
    #     return len(self.prefix) + self.unencrypted_length

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
        Decrypt value from DB if encrypted, else return value
        """
        # if isinstance(self.crypt.primary_key, keyczar.keys.RsaPublicKey):
        #     retval = value
        if self.running_as_test:
            return value

        if value and not isinstance(value, datetime.date): 
            if (value.startswith(self.prefix)):
                # Decrypt
                decrypt_data_response = self.client.secrets.transit.decrypt_data(
                    name=self.vault_transit_key,
                    ciphertext=value,
                )
                plaintext = decrypt_data_response['data']['plaintext']
                # print(plaintext)

                retval = base64.b64decode(plaintext).decode('utf-8')
                if self.data_type == 'date':
                    # Transform return value into datetime.date
                    [year, month, day] = retval.split('-')
                    retval = datetime.date(int(year), int(month), int(day))
            else:
                # We have an unencrypted string in the DB.
                # It'll be encrypted the next time it's saved
                # This allows migrating unencrypted fields to encrypted fields
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
        # if value and not value.startswith(self.prefix):
        if self.running_as_test:
            return value

        if value:
            if self.data_type == 'date':
                plaintext = str(value)  # convert to string first
            else:
                plaintext = value

            if plaintext.startswith(self.prefix):
                # Just in case, make sure we never double encrypt
                return value

            # Truncated encrypted content is unreadable,
            # so truncate before encryption
            # max_length = self.unencrypted_length
            # if max_length and len(plaintext) > max_length:
            #     warnings.warn("Truncating field %s from %d to %d bytes" % (
            #         self.name, len(plaintext), max_length), EncryptionWarning
            #     )
            #     plaintext = plaintext[:max_length]

            # plaintext.encode created a bytestring
            # Don't use urlsafe encode, Vault doesn't like it.

            encrypt_data_response = self.client.secrets.transit.encrypt_data(
                name=self.vault_transit_key,
                plaintext=base64.b64encode(plaintext.encode()).decode('ascii'),
            )
            # print(encrypt_data_response)

            value = encrypt_data_response['data']['ciphertext']  # (ciphertext)
            # print(value)

        return value

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
        # Only include data_type if it's not the default
        if self.data_type != 'string':
            kwargs['data_type'] = self.data_type
        return name, path, args, kwargs


class EncryptedTextField(BaseEncryptedField):
    def get_internal_type(self):
        return 'TextField'

    # def formfield(self, **kwargs):
    #     defaults = {'widget': forms.Textarea}
    #     defaults.update(kwargs)
    #     return super(EncryptedTextField, self).formfield(**defaults)


class EncryptedCharField(BaseEncryptedField):
    def __init__(self, *args, **kwargs):
        super(EncryptedCharField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    # def formfield(self, **kwargs):
    #     defaults = {'max_length': self.max_length}
    #     defaults.update(kwargs)
    #     return super(EncryptedCharField, self).formfield(**defaults)