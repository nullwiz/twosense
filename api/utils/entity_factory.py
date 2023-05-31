# Description: Factory for creating entities from documents
from api.domain.models import Vote, Poll, User, Option

def entity_factory(document):
    entity_type = document.pop("_type")

    if entity_type == "Vote":
        return Vote(**document)
    elif entity_type == "Poll":
        return Poll(**document)
    elif entity_type == "User":
        return User(**document)
    elif entity_type == "Option":
        return Option(**document)
    else:
        raise ValueError(f"Unknown entity type {entity_type}")

