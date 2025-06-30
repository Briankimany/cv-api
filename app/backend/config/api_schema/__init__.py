from .auth import (LoginSchema ,
                   RegistrationSchema ,
                   TokenRevokeSchema,
                   TokenIssueSchema,
                   TokenListSchema)

from .education import (
    EducationCreateSchema,
    EducationDeleteSchema,
    EducationUpdateSchema
)

from .work import (
    WorkCreateSchema,
    WorkDeleteSchema,
    WorkUpdateSchema
)

from .user_optional import (
    OptionalCreateSchema,
    OptionalDeleteSchema,
    OptionalUpdateSchema
)
__all__ = [
    'LoginSchema',
    'RegistrationSchema',
    'TokenRevokeSchema',
    'TokenIssueSchema',
    'TokenListSchema',
    
    'EducationCreateSchema',
    'EducationDeleteSchema',
    'EducationUpdateSchema',

    'WorkCreateSchema',
    'WorkDeleteSchema',
    'WorkUpdateSchema',

    'OptionalCreateSchema',
    'OptionalDeleteSchema',
    'OptionalUpdateSchema'
]