"""Add analysis, webhooks, and event models

Revision ID: 003
Revises: 002
Create Date: 2024-11-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create webhooks table
    op.create_table(
        "webhooks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("event_types", sa.JSON(), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_triggered_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_webhooks_user_id", "webhooks", ["user_id"])
    op.create_index("ix_webhooks_is_active", "webhooks", ["is_active"])

    # Create recording_analysis table
    op.create_table(
        "recording_analysis",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recording_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("transcription_text", sa.Text(), nullable=True),
        sa.Column("transcription_language", sa.String(10), nullable=False, server_default="unknown"),
        sa.Column("transcription_confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("num_speakers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("clarity_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("noise_level_db", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("snr_db", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("overall_quality", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("detected_emotions", sa.JSON(), nullable=True),
        sa.Column("speaker_segments", sa.JSON(), nullable=True),
        sa.Column("detected_ads", sa.JSON(), nullable=True),
        sa.Column("processing_time_seconds", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("analysis_engine", sa.String(50), nullable=False, server_default="combined"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recording_analysis_user_id", "recording_analysis", ["user_id"])
    op.create_index("ix_recording_analysis_recording_id", "recording_analysis", ["recording_id"])

    # Create event_logs table
    op.create_table(
        "event_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_logs_user_id", "event_logs", ["user_id"])
    op.create_index("ix_event_logs_event_type", "event_logs", ["event_type"])
    op.create_index("ix_event_logs_resource_id", "event_logs", ["resource_id"])
    op.create_index("ix_event_logs_created_at", "event_logs", ["created_at"])

    # Create playback_history table
    op.create_table(
        "playback_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("station_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("station_name", sa.String(200), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("bitrate", sa.Integer(), nullable=True),
        sa.Column("skip_ads", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("started_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_playback_history_user_id", "playback_history", ["user_id"])
    op.create_index("ix_playback_history_station_id", "playback_history", ["station_id"])
    op.create_index("ix_playback_history_created_at", "playback_history", ["created_at"])

    # Create ad_feedback table
    op.create_table(
        "ad_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recording_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("start_time", sa.Float(), nullable=False),
        sa.Column("end_time", sa.Float(), nullable=False),
        sa.Column("feedback_type", sa.String(50), nullable=False),
        sa.Column("confidence_before", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ad_feedback_user_id", "ad_feedback", ["user_id"])
    op.create_index("ix_ad_feedback_recording_id", "ad_feedback", ["recording_id"])
    op.create_index("ix_ad_feedback_created_at", "ad_feedback", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_ad_feedback_created_at", table_name="ad_feedback")
    op.drop_index("ix_ad_feedback_recording_id", table_name="ad_feedback")
    op.drop_index("ix_ad_feedback_user_id", table_name="ad_feedback")
    op.drop_table("ad_feedback")

    op.drop_index("ix_playback_history_created_at", table_name="playback_history")
    op.drop_index("ix_playback_history_station_id", table_name="playback_history")
    op.drop_index("ix_playback_history_user_id", table_name="playback_history")
    op.drop_table("playback_history")

    op.drop_index("ix_event_logs_created_at", table_name="event_logs")
    op.drop_index("ix_event_logs_resource_id", table_name="event_logs")
    op.drop_index("ix_event_logs_event_type", table_name="event_logs")
    op.drop_index("ix_event_logs_user_id", table_name="event_logs")
    op.drop_table("event_logs")

    op.drop_index("ix_recording_analysis_recording_id", table_name="recording_analysis")
    op.drop_index("ix_recording_analysis_user_id", table_name="recording_analysis")
    op.drop_table("recording_analysis")

    op.drop_index("ix_webhooks_is_active", table_name="webhooks")
    op.drop_index("ix_webhooks_user_id", table_name="webhooks")
    op.drop_table("webhooks")
