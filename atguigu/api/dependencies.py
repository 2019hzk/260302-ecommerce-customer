"""
统一管理所有xxxservice

"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from atguigu.services.dialogue_service import DialogueService
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_repository import DialogueRepository
from atguigu.infrastructure.database import session_factory


def get_dialogue_engine():
    return  DialogueEngine()

DialogueEngineDep = Annotated[DialogueEngine, Depends(get_dialogue_engine)]


async def get_session():
    async with session_factory() as session:
        yield session  # return session:不能用return
        # 逻辑1
        # 逻辑2

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_dialogue_repository(session: SessionDep):
    return DialogueRepository(session)

DialogueRepositoryDep = Annotated[DialogueRepository, Depends(get_dialogue_repository)]


def get_dialogue_service(engine: DialogueEngineDep, repository: DialogueRepositoryDep):
    return DialogueService(engine, repository)

DialogueServiceDep = Annotated[DialogueService, Depends(get_dialogue_service)]