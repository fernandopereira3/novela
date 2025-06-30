from pydantic import BaseModel


class UserSchema(BaseModel):
    username: str
    email: str
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: str

    def dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email}
