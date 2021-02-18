ALLOWED_PROFILE_IMAGE_FORMATS = ['image/png', 'image/jpg', 'image/jpeg']
ALLOWED_FILE_FORMATS = ['image/png', 'image/jpg', 'image/jpeg', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']

STRIPE_RETURN_URL = 'https://www.bitsybits.com/login/'
STRIPE_REFRESH_URL = 'https://www.bitsybits.com/'

# 3 mb, written in bytes
MAX_PROFILE_IMAGE_SIZE = 3145728 

MAX_MEDIA_ALLOWED = 10
MAX_MEDIA_SIZE = 1024*1024*10

MAX_QUESTION_SIZE = 250
MAX_BIO_LENGTH = 140

MAX_VALIDITY_DAYS = 30
MAX_ANSWER_LIMIT = 15
MIN_ANSWER_LIMIT = 1

REQUEST_TYPE = (
    ('post','Post'),
    ('edit','Edit'),
    ('delete','Delete'),
)

# rating of question author above which a user cannot flag it as spammed.
# X_RATING = 4

# in percentage
# SECURITY_AMOUNT_RATE = 10
# SERVICE_CHARGE_RATE = 10

USER_STATUS = (
    ('Activated','Activated'),
    ('Blocked','Blocked'),
    ('Deleted','Deleted')
)

# User gender
# GENDER = (
#     ('Male','Male'),
#     ('Female','Female'),
#     ('Other','Other')
# )

# Report user status
REPORT_STATUS = (
    ('pending','pending'),
    ('resolved','resolved'),
    ('discarded','discarded')
)

# CURRENCY = (
#     ('usd', 'usd'),
#     ('pounds', 'pounds')
# )

CATEGORY_STATUS = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive')
)

QUESTION_STATUS = (
    ('pending', 'Pending'),
    ('deleted', 'Deleted'),
    ('open', 'Open'),
    ('waiting', 'waiting'),
    ('spammed', 'Spammed'),
)

# PAYMENT_STATUS = (
#     ('not_paid', 'NOT_PAID'),
#     ('paid', 'PAID'),
#     ('failed', 'Failed'),
# )

ANSWER_STATUS = (
    ('open', 'Open'),
    ('Deleted', 'Deleted'),
    ('pending', 'pending'),
    ('spammed', 'Spammed'),
)

# REFUND_STATUS = (
#     ('requested', 'Requested'),
#     ('rejected', 'Rejected'),
#     ('processed', 'Processed')
# )

REACTION_TYPE = (
    ('Like', 'Like'),
    ('Dislike', 'Dislike'),
)

SPAMMED_STATUS = (
    ('pending', 'Pending'),
    ('rejected', 'Rejected'),
    ('accepted', 'Accepted'),
)

VOTE_CHOICES = (
    ('upvote', 'Upvote'),
    ('downvoye', 'Downvote'),
)

OPEN_QUESTION_LIMIT = 10
OPEN_ANSWER_LIMIT = 10
OPEN_REPLY_LIMIT = 10

def change_qlimit(qlimit):
    global OPEN_QUESTION_LIMIT
    OPEN_QUESTION_LIMIT = qlimit
    return OPEN_QUESTION_LIMIT

def change_alimit(alimit):
    global OPEN_ANSWER_LIMIT
    OPEN_ANSWER_LIMIT = alimit
    return OPEN_ANSWER_LIMIT

def change_rlimit(rlimit):
    global OPEN_REPLY_LIMIT
    OPEN_REPLY_LIMIT = rlimit
    return OPEN_REPLY_LIMIT
