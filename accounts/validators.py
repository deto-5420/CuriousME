import re
from collectanea.globals import MAX_BIO_LENGTH, ALLOWED_PROFILE_IMAGE_FORMATS, MAX_PROFILE_IMAGE_SIZE
from django.core.exceptions import ValidationError

def username_validator(username):
    found = re.search('[^A-Za-z0-9@#_$<>]|^[^A-Za-z]|(^.{32,})', username)

    if found:
        raise ValidationError("Username must be between 4 to 32 characters and can only contain alphabets, numerals and some special characters ( @, #, _ ) and can only start with a alphabet.")

def bio_validator(bio):
    if len(bio) > MAX_BIO_LENGTH:
        raise ValidationError("Bio can be of maximum 140 characters.")

def avatar_validator(avatar):
    size = avatar.size
    file_format = avatar.content_type

    if size > MAX_PROFILE_IMAGE_SIZE:
        raise ValidationError('File size too large, max allowed file size is 10MB.')

    if file_format not in ALLOWED_PROFILE_IMAGE_FORMATS:
        raise ValidationError('File type not supported.')