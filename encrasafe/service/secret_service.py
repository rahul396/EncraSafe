import os
import base64
from uuid import uuid4
from loguru import logger
from cryptography.fernet import Fernet
from encrasafe.database import inject_db_session, db_models

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

class SecretManagerService:

    def encrypt_string(self, input_text):
        base64_key = base64.urlsafe_b64encode(ENCRYPTION_KEY.encode())
        fernet_obj = Fernet(base64_key)
        encrypted_text = fernet_obj.encrypt(input_text.encode())
        return encrypted_text.decode()
    
    def decrypt_string(self, encrypted_text):
        base64_key = base64.urlsafe_b64encode(ENCRYPTION_KEY.encode())
        fernet_obj = Fernet(base64_key)
        decoded_text = fernet_obj.decrypt(encrypted_text.encode())
        return decoded_text.decode()
    
    # @inject_db_session()
    # def set_secret(self, db_session, key, value, env='DEV'):
    #     _secret = db_models.Secrets(
    #         id=str(uuid4()),
    #         env=env,
    #         secret_name=key,
    #         secret_value=self.encrypt_string(value)
    #     )
    #     db_session.add(_secret)
    #     db_session.flush()
    #     db_session.commit()
    
    @inject_db_session()
    def get_secret(self, db_session, key, version=None, env='DEV'):
        if not version:
            # get the latest version of the secret
            _secret = db_session.query(db_models.Secrets).filter_by(
                secret_name=key,
                is_current=True,
                env=env
            ).one()
        else:
            _secret = db_session.query(db_models.Secrets).filter_by(
                secret_name=key,
                secret_version=version,
                env=env
            ).one()
        
        if _secret:
            return self.decrypt_string(_secret.secret_value)
        else:
            logger.info(f'Couldnt find the secret: {key}')
    
    @inject_db_session()
    def set_or_update_secret(self, db_session, key, value, env='DEV'):
        version = None
        old_secret = db_session.query(db_models.Secrets).filter_by(
                secret_name=key,
                is_current=True,
                env=env
            ).first()
        if old_secret:
            old_secret.is_current = False
            version = float(old_secret.secret_version) + 0.01
        # Add a new row
        _secret = db_models.Secrets(
            id=str(uuid4()),
            env=env,
            secret_name=key,
            secret_value=self.encrypt_string(value),
            secret_version=version,
        )
        db_session.add(_secret)
        db_session.flush()
        db_session.commit()
    

if __name__ == '__main__':
    sms = SecretManagerService()
    sms.set_or_update_secret('name', 'rahul')
    # import pdb;pdb.set_trace()
    logger.info('Before update..')
    logger.info(sms.get_secret('name'))
    sms.set_or_update_secret('name', 'kumar')
    logger.info('After update..')
    logger.info(sms.get_secret('name'))


        


