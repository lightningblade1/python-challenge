from fastapi import FastAPI, Request

app = FastAPI(
    title="Emilia Hiring Challenge 👩‍💻",
    description="Help Emilia 👩 to fix our tests and get a job interview 💼🎙️!",
)

"""
Task 1 - Warmup
"""


@app.get("/task1/greet/{name}", tags=["Task 1"], summary="👋🇩🇪🇬🇧🇪🇸")
async def task1_greet(name: str, request: Request) -> str:
    """Greet somebody in German, English or Spanish!"""
    # Write your code below
    if request.query_params:
        if request.query_params['language'] == 'en':
            return f"Hello {name}, I am Emilia."
        if request.query_params['language'] == 'es':
            return f"Hola {name}, soy Emilia."
        if request.query_params['language'] == 'ita':
            return f"Hallo {name}, leider spreche ich nicht 'ita'!"
    else:
        return f"Hallo {name}, ich bin Emilia."


"""
Task 2 - snake_case to cameCase
"""

from typing import Any


def camelize(key: str):
    """Takes string in snake_case format returns camelCase formatted version."""
    # Write your code below
    if len(key) == 0:
        return key
    s = key.replace("_", " ")
    s = s.split()
    return s[0] + ''.join(i.capitalize() for i in s[1:])
    return key


@app.post("/task2/camelize", tags=["Task 2"], summary="🐍➡️🐪")
async def task2_camelize(data: dict[str, Any]) -> dict[str, Any]:
    """Takes a JSON object and transfroms all keys from snake_case to camelCase."""
    return {camelize(key): value for key, value in data.items()}


"""
Task 3 - Handle User Actions
"""

from pydantic import BaseModel

friends = {
    "Matthias": ["Sahar", "Franziska", "Hans"],
    "Stefan": ["Felix", "Ben", "Philip"],
}


class ActionRequest(BaseModel):
    username: str
    action: str


class ActionResponse(BaseModel):
    message: str


contacts = {'MATTHIAS': ['SAHAR', 'HANS', 'FRANZISKA'], 'STEFAN': ['BEN']}


def handle_call_action(action):
    # Write your code below
    for ele in contacts[action.username.upper()]:
        if (ele in action.action.upper()):
            name = f"🤙 Calling {ele.capitalize()} ..."
            return {
                "message": name, }
    return {"message": f"{action.username}, I can't find this person in your contacts.", }


def handle_reminder_action(action: str):
    # Write your code below
    ...
    return {
        "message": "🔔 Alright, I will remind you!",
    }


def handle_timer_action(action: str):
    # Write your code below
    ...
    return {
        "message": "⏰ Alright, the timer is set!",
    }


def handle_unknown_action(action: str):
    # Write your code below
    ...
    return {
        "message": "👀 Sorry , but I can't help with that!",
    }


@app.post("/task3/action", tags=["Task 3"], summary="🤌")
def task3_action(request: ActionRequest):
    """Accepts an action request, recognizes its intent and forwards it to the corresponding action handler."""
    # tip: you have to use the response model above and also might change the signature
    #      of the action handlers
    # Write your code below
    ...
    from random import choice

    # There must be a better way!
    if request.username.upper() in contacts.keys():

        if 'CALL' in request.action.upper():  # capitalise because old people can make mistakes while typing and mix small and capital letters
            handler = handle_call_action
        elif 'REMIND' in request.action.upper():
            handler = handle_reminder_action
        elif 'TIMER' in request.action.upper():
            handler = handle_timer_action
        else:
            handler = handle_unknown_action
        return handler(request)

    return {"message": f"Hi {request.username}, I don't know you yet. But I would love to meet you!", }


"""
Task 4 - Security
"""

from datetime import datetime, timedelta
from functools import partial
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

# create secret key with: openssl rand -hex 32
SECRET_KEY = "069d49a9c669ddc08f496352166b7b5d270ff64d3009fc297689aa8b0fb66d98"
ALOGRITHM = "HS256"

encode_jwt = partial(jwt.encode, key=SECRET_KEY, algorithm=ALOGRITHM)
decode_jwt = partial(jwt.decode, key=SECRET_KEY, algorithms=[ALOGRITHM])

_crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
verify_password = _crypt_context.verify
hash_password = _crypt_context.hash

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/task4/token")

fake_users_db = {
    "stefan": {
        "username": "stefan",
        "email": "stefan.buchkremer@meetap.de",
        "hashed_password": hash_password("decent-espresso-by-john-buckmann"),
        "secret": "I love pressure-profiled espresso ☕!",
    },
    "felix": {
        "username": "felix",
        "email": "felix.andreas@meetap.de",
        "hashed_password": hash_password("elm>javascript"),
        "secret": "Rust 🦀 is the best programming language ever!",
    },
}


class User(BaseModel):
    username: str
    email: str
    hashed_password: str
    secret: str


class Token(BaseModel):
    access_token: str
    token_type: str


@app.post("/task4/token", response_model=Token, summary="🔒", tags=["Task 4"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Allows registered users to obtain a bearer token."""
    # fixme 🔨, at the moment we allow everybody to obtain a token
    # this is probably not very secure 🛡️ ...
    # tip: check the verify_password above
    # Write your code below
    ...
    payload = {
        "sub": form_data.username,
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    if form_data.username in fake_users_db:
        if verify_password(form_data.password, fake_users_db[form_data.username]["hashed_password"]):
            return {
                "access_token": encode_jwt(payload),
                "token_type": "bearer",
            }
    raise HTTPException(status_code=401, detail="Incorrect username or password")


def get_user(username: str) -> Optional[User]:
    if username not in fake_users_db:
        return
    return User(**fake_users_db[username])


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return decode_jwt(token)
    # check if the token 🪙 is valid and return a user as specified by the tokens payload
    # otherwise raise the credentials_exception above
    # Write your code below
    ...


@app.get("/task4/users/{username}/secret", summary="🤫", tags=["Task 4"])
async def read_user_secret(
        username: str, current_user: User = Depends(get_current_user)
):
    """Read a user's secret."""
    # uppps 🤭 maybe we should check if the requested secret actually belongs to the user
    # Write your code below
    ...

    if user := get_user(username):
        if current_user['sub'] == user.username:
            return user.secret
        else:
            raise HTTPException(status_code=403, detail="Don't spy on other user!")


"""
Task and Help Routes
"""

from functools import partial
from pathlib import Path

from tomlkit.api import parse

messages = parse((Path(__file__).parent / "messages.toml").read_text("utf-8"))


@app.get("/", summary="👋", tags=["Emilia"])
async def hello():
    return messages["hello"]


identity = lambda x: x
for i in 1, 2, 3, 4:
    task = messages[f"task{i}"]
    info = partial(identity, task["info"])
    help_ = partial(identity, task["help"])
    tags = [f"Task {i}"]
    app.get(f"/task{i}", summary="📝", description=info(), tags=tags)(info)
    app.get(f"/task{i}/help", summary="🙋", description=help_(), tags=tags)(help_)
