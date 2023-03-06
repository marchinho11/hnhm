from hnhm import Layout, HnhmLink, HnhmLinkElement

from .user import User
from .review import Review


class LinkUserReview(HnhmLink):
    """Links User with Review."""

    __layout__ = Layout(name="user_review")

    user = HnhmLinkElement(entity=User(), comment="User")
    review = HnhmLinkElement(entity=Review(), comment="Review")

    __keys__ = [user, review]
