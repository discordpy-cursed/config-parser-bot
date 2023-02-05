from typing import Dict, Optional

from pydantic import BaseModel


class Category(BaseModel):
    description: Optional[str]
    commands: list[str]


class Command(BaseModel):
    name: Optional[str]
    description: Optional[str]
    aliases: Optional[list[str]]
    parent: Optional[str]


class Config(BaseModel):
    category: Dict[str, Category]
    command: Dict[str, Command]
