from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from packages.db_schema.models import WarRoom, WarRoomMessage
from app.schemas.entities import (
    WarRoomCreate,
    WarRoomRead,
    WarRoomMessageCreate,
    WarRoomMessageRead
)
from app.core.state_machine import OrchestratorStateMachine, StateMachineError

router = APIRouter(prefix="/war-rooms", tags=["War Rooms & Consultant Protocol"])

@router.post("", response_model=WarRoomRead)
async def create_war_room(payload: WarRoomCreate, db: AsyncSession = Depends(get_db)):
    try:
        war_room, accepted, rejected = await OrchestratorStateMachine.create_war_room_and_invite(
            db=db,
            initiator_agent_id=payload.initiator_agent_id,
            task_id=payload.task_id,
            title=payload.title,
            invitee_agent_ids=payload.invitee_agent_ids,
            correlation_id=payload.correlation_id
        )
        await db.commit()
        await db.refresh(war_room)

        return WarRoomRead(
            id=war_room.id,
            task_id=war_room.task_id,
            title=war_room.title,
            initiator_agent_id=war_room.initiator_agent_id,
            status=war_room.status,
            created_at=war_room.created_at,
            concluded_at=war_room.concluded_at,
            accepted_agents=accepted,
            rejected_agents=rejected
        )
    except StateMachineError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{war_room_id}/messages", response_model=WarRoomMessageRead)
async def post_war_room_message(
    war_room_id: str,
    payload: WarRoomMessageCreate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WarRoom).where(WarRoom.id == war_room_id)
    res = await db.execute(stmt)
    wr = res.scalar_one_or_none()
    if not wr:
        raise HTTPException(status_code=404, detail="War Room not found")

    if wr.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Cannot post to War Room in status '{wr.status}'")

    msg = WarRoomMessage(
        war_room_id=war_room_id,
        sender_type=payload.sender_type,
        agent_id=payload.agent_id,
        content=payload.content,
        correlation_id=payload.correlation_id
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

@router.get("/{war_room_id}/messages", response_model=List[WarRoomMessageRead])
async def list_war_room_messages(war_room_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(WarRoomMessage).where(WarRoomMessage.war_room_id == war_room_id).order_by(WarRoomMessage.created_at.asc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/{war_room_id}/conclude", response_model=WarRoomRead)
async def conclude_war_room(
    war_room_id: str,
    correlation_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        wr = await OrchestratorStateMachine.conclude_war_room(
            db=db,
            war_room_id=war_room_id,
            correlation_id=correlation_id
        )
        await db.commit()
        await db.refresh(wr)
        return WarRoomRead(
            id=wr.id,
            task_id=wr.task_id,
            title=wr.title,
            initiator_agent_id=wr.initiator_agent_id,
            status=wr.status,
            created_at=wr.created_at,
            concluded_at=wr.concluded_at,
            accepted_agents=[],
            rejected_agents=[]
        )
    except StateMachineError as e:
        raise HTTPException(status_code=400, detail=str(e))
