"""Add CBS radio stations seed data

Revision ID: 002
Revises: 001
Create Date: 2024-09-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create CBS radio stations
    connection = op.get_bind()

    # CBS 기독교방송 라디오 방송국 데이터
    cbs_stations = [
        {
            'id': str(uuid.uuid4()),
            'name': 'CBS 표준FM',
            'stream_url': 'https://m-aac.cbs.co.kr/mweb_cbs981/_definst_/cbs981.stream/chunklist.m3u8',
            'description': 'CBS 기독교방송 표준FM 98.1MHz',
            'genre': '종교방송',
            'country': '대한민국',
            'language': '한국어'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'CBS 음악FM',
            'stream_url': 'https://m-aac.cbs.co.kr/mweb_cbs939/_definst_/cbs939.stream/chunklist.m3u8',
            'description': 'CBS 기독교방송 음악FM 93.9MHz',
            'genre': '종교음악',
            'country': '대한민국',
            'language': '한국어'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'CBS Joy4You',
            'stream_url': 'https://m-aac.cbs.co.kr/mweb_cbscmc/_definst_/cbscmc.stream/chunklist.m3u8',
            'description': 'CBS 기독교방송 Joy4You',
            'genre': '종교방송',
            'country': '대한민국',
            'language': '한국어'
        },
        # Alternative URLs (backup)
        {
            'id': str(uuid.uuid4()),
            'name': 'CBS 표준FM (backup)',
            'stream_url': 'http://aac.cbs.co.kr/cbs981/_definst_/cbs981.stream/playlist.m3u8',
            'description': 'CBS 기독교방송 표준FM 98.1MHz (백업 URL)',
            'genre': '종교방송',
            'country': '대한민국',
            'language': '한국어'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'CBS 음악FM (backup)',
            'stream_url': 'http://aac.cbs.co.kr/cbs939/_definst_/cbs939.stream/playlist.m3u8',
            'description': 'CBS 기독교방송 음악FM 93.9MHz (백업 URL)',
            'genre': '종교음악',
            'country': '대한민국',
            'language': '한국어'
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'CBS Joy4You (backup)',
            'stream_url': 'http://aac.cbs.co.kr/cbscmc/_definst_/cbscmc_96k.stream/playlist.m3u8',
            'description': 'CBS 기독교방송 Joy4You (백업 URL)',
            'genre': '종교방송',
            'country': '대한민국',
            'language': '한국어'
        }
    ]

    # Insert CBS stations
    for station in cbs_stations:
        connection.execute(
            sa.text("""
                INSERT INTO radio_stations
                (id, name, stream_url, description, genre, country, language, created_at, updated_at)
                VALUES
                (:id, :name, :stream_url, :description, :genre, :country, :language, now(), now())
            """),
            station
        )


def downgrade() -> None:
    # Remove CBS stations
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM radio_stations WHERE name LIKE 'CBS%'")
    )