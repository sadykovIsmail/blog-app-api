from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class RegisterThrottle(AnonRateThrottle):
    scope = 'register'


class CommentThrottle(UserRateThrottle):
    scope = 'comments'


class FollowThrottle(UserRateThrottle):
    scope = 'follows'


class EvidenceThrottle(AnonRateThrottle):
    scope = 'evidence'
