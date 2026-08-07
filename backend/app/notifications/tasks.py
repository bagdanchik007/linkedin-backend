from app.core.celery_app import celery_app
from app.core.database import async_session_maker
from app.notifications.service import create_notification


@celery_app.task(name="notifications.on_connection_request")
def notify_connection_request(receiver_id: str, requester_id: str, requester_email: str):
    """
    Hintergrundjob: Benachrichtigung senden wenn jemand eine Verbindungsanfrage schickt.
    Wird von Celery Worker asynchron ausgeführt.
    """
    import asyncio
    asyncio.run(_notify_connection_request(receiver_id, requester_id, requester_email))


async def _notify_connection_request(
    receiver_id: str,
    requester_id: str,
    requester_email: str,
):
    async with async_session_maker() as db:
        await create_notification(
            db=db,
            user_id=receiver_id,
            type="connection_request",
            payload={
                "requester_id": requester_id,
                "requester_email": requester_email,
            },
        )


@celery_app.task(name="notifications.on_application_update")
def notify_application_update(
    applicant_id: str,
    job_title: str,
    new_status: str,
):
    """
    Hintergrundjob: Bewerber benachrichtigen wenn sein Bewerbungsstatus sich ändert.
    Z.B. 'accepted' oder 'rejected'.
    """
    import asyncio
    asyncio.run(_notify_application_update(applicant_id, job_title, new_status))


async def _notify_application_update(
    applicant_id: str,
    job_title: str,
    new_status: str,
):
    async with async_session_maker() as db:
        await create_notification(
            db=db,
            user_id=applicant_id,
            type="application_update",
            payload={
                "job_title": job_title,
                "new_status": new_status,
            },
        )


@celery_app.task(name="notifications.on_new_job")
def notify_new_job(user_id: str, job_id: str, job_title: str, company: str):
    """
    Hintergrundjob: Benutzer benachrichtigen wenn eine passende Stelle veröffentlicht wird.
    Wird ausgelöst wenn die Stelle Skills des Benutzers enthält.
    """
    import asyncio
    asyncio.run(_notify_new_job(user_id, job_id, job_title, company))


async def _notify_new_job(
    user_id: str,
    job_id: str,
    job_title: str,
    company: str,
):
    async with async_session_maker() as db:
        await create_notification(
            db=db,
            user_id=user_id,
            type="new_job",
            payload={
                "job_id": job_id,
                "job_title": job_title,
                "company": company,
            },
        )
