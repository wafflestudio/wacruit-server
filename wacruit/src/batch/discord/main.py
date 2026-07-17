import httpx
from loguru import logger

from wacruit.src.apps.member.config import discord_config
from wacruit.src.apps.member.models import DiscordMember
from wacruit.src.database.connection import DBSessionFactory

MAX_THRESHOLD = 1000


def fetch_discord_members() -> list[dict]:
    discord_bot_token = discord_config.discord_bot_token
    discord_guild_id = discord_config.discord_guild_id

    if not discord_bot_token or not discord_guild_id:
        logger.error(
            "DISCORD_BOT_TOKEN and DISCORD_GUILD_ID must be configured in settings/env."
        )
        return []

    logger.info("Starting to fetch members from Discord Guild...")
    members = []
    after = None
    headers = {"Authorization": f"Bot {discord_bot_token}"}

    with httpx.Client() as client:
        while True:
            url = f"https://discord.com/api/v10/guilds/{discord_guild_id}/members?limit={MAX_THRESHOLD}"
            if after:
                url += f"&after={after}"

            try:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"HTTP request to Discord failed: {e}")
                raise e

            if not data:
                break

            members.extend(data)
            after = data[-1]["user"]["id"]

            if len(data) < MAX_THRESHOLD:
                break

    logger.info(f"Successfully fetched {len(members)} members from Discord.")
    return members


def sync_discord_members():
    fetched_members = fetch_discord_members()
    if not fetched_members:
        logger.warning("No members fetched. Sync aborted.")
        return

    session = DBSessionFactory().make_session()
    try:
        db_members = session.query(DiscordMember).all()
        db_members_map = {m.discord_id: m for m in db_members}

        fetched_ids = set()

        for member in fetched_members:
            user = member.get("user")
            if not user:
                continue

            discord_id = user["id"]
            fetched_ids.add(discord_id)

            name = (
                member.get("nick")
                or user.get("global_name")
                or user.get("username")
                or "Unknown"
            )
            name = name[:30]

            if discord_id in db_members_map:
                db_member = db_members_map[discord_id]
                if db_member.name != name:
                    db_member.name = name
            else:
                new_member = DiscordMember(
                    discord_id=discord_id,
                    name=name,
                    slack_user_id=None,
                    github_username=None,
                )
                session.add(new_member)

        for discord_id, db_member in db_members_map.items():
            if discord_id not in fetched_ids:
                logger.info(
                    f"Removing member: {db_member.name} (Discord ID: {discord_id})"
                )
                session.delete(db_member)

        session.commit()
        logger.info("Discord member sync completed successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Discord member sync failed: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    sync_discord_members()
