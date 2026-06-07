from app.db.base import Base
from app.models import CreditLedger, Transcript, TranscriptionJob, User


def test_database_models_are_registered():
    table_names = set(Base.metadata.tables.keys())

    assert "users" in table_names
    assert "transcription_jobs" in table_names
    assert "transcripts" in table_names
    assert "credit_ledger" in table_names


def test_user_model_has_required_columns():
    users_table = Base.metadata.tables["users"]

    assert "id" in users_table.columns
    assert "email" in users_table.columns
    assert "password_hash" in users_table.columns
    assert "credit_balance" in users_table.columns


def test_transcription_job_model_has_required_columns():
    jobs_table = Base.metadata.tables["transcription_jobs"]

    assert "id" in jobs_table.columns
    assert "user_id" in jobs_table.columns
    assert "original_filename" in jobs_table.columns
    assert "provider" in jobs_table.columns
    assert "status" in jobs_table.columns


def test_transcript_model_has_required_columns():
    transcripts_table = Base.metadata.tables["transcripts"]

    assert "id" in transcripts_table.columns
    assert "job_id" in transcripts_table.columns
    assert "text" in transcripts_table.columns


def test_credit_ledger_model_has_required_columns():
    credit_table = Base.metadata.tables["credit_ledger"]

    assert "id" in credit_table.columns
    assert "user_id" in credit_table.columns
    assert "amount" in credit_table.columns
    assert "balance_after" in credit_table.columns
    assert "reason" in credit_table.columns
