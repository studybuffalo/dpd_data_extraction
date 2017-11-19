# Setup a module-wide object containing the substitution data
from hc_dpd.models import (
    SubAHFS
)

class SubList(object):
    """An object of lists of original text and index-matched subs"""
    def __init__(self, original, substitution):
        self.original = original
        self.substitution = substitution

def generate_sub_list(model):
    """Converts Django sub data model to a SubList object"""
    original = []
    substitution = []

    for item in model.objects.all.order_by("original"):
        original.append(item.original)
        substitution.append(item.substitution)

    return SubList(original, substitution)


class Substitutions(object):
    def __init__(self):
        self.ahfs = generate_sub_list(SubAHFS)
