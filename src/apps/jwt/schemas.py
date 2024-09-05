from pydantic import BaseModel


class AccessTokenOutputSchema(BaseModel):
    access_token: str
    is_staff: str
    can_recept_stocks: str
    can_move_stocks: str
    can_issue_stocks: str


class ConfirmationTokenSchema(BaseModel):
    token: str
