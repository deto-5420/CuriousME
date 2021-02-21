from dynamic_preferences.types import IntegerPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry

# we create some section objects to link related preferences together
open = Section('open')

# We start with a global preference
@global_preferences_registry.register
class QuestionLimit(IntegerPreference):
    section = open
    name = 'QUESTION_LIMIT'
    default = 10
    required = False

@global_preferences_registry.register
class AnswerLimit(IntegerPreference):
    section = open
    name = 'ANSWER_LIMIT'
    default = 10
    required = False

@global_preferences_registry.register
class ReplyLimit(IntegerPreference):
    section = open
    name = 'REPLY_LIMIT'
    default = 10
    required = False