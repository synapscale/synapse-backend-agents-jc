#!/usr/bin/env python3
"""
LLM Data Migration Script - Database Migration Plan Implementation
Ensures data consistency between existing enums and the database.

This script provides migration and validation utilities for the LLM unification project:
1. Analyzes existing enums and database schema
2. Identifies missing data in the database  
3. Creates migration scripts to ensure all enum values exist in the database
4. Implements validation to ensure consistency
5. Handles data discrepancies and provides migration paths

Usage:
    python src/synapse/scripts/migrate_llm_data.py migrate
    python src/synapse/scripts/migrate_llm_data.py validate
    python src/synapse/scripts/migrate_llm_data.py analyze
    python src/synapse/scripts/migrate_llm_data.py sync-enums

Created for task #9 "Create Database Migration Plan" in llm-unification project
"""

import os
import sys
import click
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add src to path for imports
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(BASE_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from synapse.database import get_db
from synapse.models.llm import LLM
from synapse.core.config import settings
from synapse.api.v1.endpoints.llm.schemas import ModelEnum, ProviderEnum


@dataclass
class ModelMapping:
    """Represents a model-provider mapping from enums"""

    model_id: str
    provider: str
    enum_name: str


@dataclass
class MigrationReport:
    """Report of migration analysis"""

    enum_models: List[ModelMapping]
    db_models: List[Dict]
    missing_in_db: List[ModelMapping]
    missing_in_enum: List[Dict]
    inconsistencies: List[str]
    total_enum_models: int
    total_db_models: int


# Model-Provider mapping based on enum naming conventions and known associations
ENUM_MODEL_PROVIDER_MAPPING = {
    # OpenAI models
    "gpt-4o": "openai",
    "gpt-4-turbo": "openai",
    "gpt-3.5-turbo": "openai",
    # Claude models (Anthropic)
    "claude-3-opus-20240229": "anthropic",
    "claude-3-sonnet-20240229": "anthropic",
    "claude-3-haiku-20240307": "anthropic",
    # Gemini models (Google)
    "gemini-1.5-pro": "google",
    "gemini-1.5-flash": "google",
    # Llama models (Meta)
    "llama-3-70b": "llama",
    "llama-3-8b": "llama",
    "llama-2-70b": "llama",
    # Grok models (xAI)
    "grok-1": "grok",
    # DeepSeek models
    "deepseek-chat": "deepseek",
    "deepseek-coder": "deepseek",
}


def get_enum_models() -> List[ModelMapping]:
    """Extract all models from ModelEnum with their provider mappings."""
    models = []

    for model_enum in ModelEnum:
        model_id = model_enum.value
        enum_name = model_enum.name

        # Determine provider from the mapping or enum name pattern
        if model_id in ENUM_MODEL_PROVIDER_MAPPING:
            provider = ENUM_MODEL_PROVIDER_MAPPING[model_id]
        else:
            # Fallback: infer from enum name prefix
            if enum_name.startswith(("gpt_", "openai_")):
                provider = "openai"
            elif enum_name.startswith("claude_"):
                provider = "anthropic"
            elif enum_name.startswith("gemini_"):
                provider = "google"
            elif enum_name.startswith("llama_"):
                provider = "llama"
            elif enum_name.startswith("grok_"):
                provider = "grok"
            elif enum_name.startswith("deepseek_"):
                provider = "deepseek"
            else:
                provider = "unknown"

        models.append(
            ModelMapping(model_id=model_id, provider=provider, enum_name=enum_name)
        )

    return models


def get_database_models(db_session: Session) -> List[Dict]:
    """Get all models from database."""
    try:
        models = db_session.query(LLM).all()
        return [
            {
                "id": str(model.id),
                "name": model.name,
                "provider": model.provider,
                "model_version": model.model_version,
                "is_active": model.is_active,
                "created_at": model.created_at,
                "supports_function_calling": model.supports_function_calling,
                "supports_vision": model.supports_vision,
                "context_window": model.context_window,
                "cost_per_token_input": model.cost_per_token_input,
                "cost_per_token_output": model.cost_per_token_output,
            }
            for model in models
        ]
    except Exception as e:
        click.echo(f"❌ Error querying database: {e}")
        return []


def analyze_migration_gaps(db_session: Session) -> MigrationReport:
    """Analyze gaps between enums and database."""
    click.echo("🔍 Analyzing migration gaps between enums and database...")

    # Get data from both sources
    enum_models = get_enum_models()
    db_models = get_database_models(db_session)

    # Create lookup sets for comparison
    enum_lookup = {(model.model_id, model.provider) for model in enum_models}
    db_lookup = {(model["name"], model["provider"]) for model in db_models}

    # Find missing in database
    missing_in_db = []
    for enum_model in enum_models:
        if (enum_model.model_id, enum_model.provider) not in db_lookup:
            missing_in_db.append(enum_model)

    # Find missing in enums (database models not in enums)
    missing_in_enum = []
    for db_model in db_models:
        if (db_model["name"], db_model["provider"]) not in enum_lookup:
            missing_in_enum.append(db_model)

    # Find inconsistencies (same model but different details)
    inconsistencies = []
    for enum_model in enum_models:
        matching_db_models = [
            db_model
            for db_model in db_models
            if db_model["name"] == enum_model.model_id
            and db_model["provider"] == enum_model.provider
        ]

        if matching_db_models:
            db_model = matching_db_models[0]
            if not db_model["is_active"]:
                inconsistencies.append(
                    f"Model {enum_model.model_id} ({enum_model.provider}) is inactive in database but active in enum"
                )

    return MigrationReport(
        enum_models=enum_models,
        db_models=db_models,
        missing_in_db=missing_in_db,
        missing_in_enum=missing_in_enum,
        inconsistencies=inconsistencies,
        total_enum_models=len(enum_models),
        total_db_models=len(db_models),
    )


def migrate_enum_models_to_database(
    db_session: Session, report: MigrationReport
) -> int:
    """Migrate missing enum models to database."""
    if not report.missing_in_db:
        click.echo("✅ No enum models missing in database")
        return 0

    click.echo(f"📥 Adding {len(report.missing_in_db)} missing models to database...")

    models_to_add = []

    for enum_model in report.missing_in_db:
        # Create basic model entry with sensible defaults
        # Note: Real pricing/capabilities should be updated manually or via populate script
        new_model = LLM(
            id=uuid.uuid4(),
            name=enum_model.model_id,
            provider=enum_model.provider,
            model_version="latest",  # Default version
            cost_per_token_input=0.001,  # Conservative default
            cost_per_token_output=0.001,  # Conservative default
            max_tokens_supported=4096,  # Safe default
            supports_function_calling=True,  # Most modern models support this
            supports_vision=False,  # Conservative default
            supports_streaming=True,  # Most models support this
            context_window=8192,  # Common default
            is_active=True,
            llm_metadata={
                "description": f"Model {enum_model.model_id} from {enum_model.provider}",
                "source": "enum_migration",
                "migrated_at": datetime.utcnow().isoformat(),
                "enum_name": enum_model.enum_name,
                "note": "Default values - update with real specifications",
            },
        )
        models_to_add.append(new_model)

    try:
        db_session.add_all(models_to_add)
        db_session.commit()
        click.echo(f"✅ Successfully added {len(models_to_add)} models to database")
        return len(models_to_add)
    except Exception as e:
        db_session.rollback()
        click.echo(f"❌ Error adding models to database: {e}")
        return 0


def validate_database_enum_consistency(db_session: Session) -> bool:
    """Validate consistency between enums and database."""
    click.echo("🔍 Validating consistency between enums and database...")

    report = analyze_migration_gaps(db_session)

    # Display validation results
    click.echo(f"\n📊 Validation Results:")
    click.echo(f"   Enum models: {report.total_enum_models}")
    click.echo(f"   Database models: {report.total_db_models}")
    click.echo(f"   Missing in database: {len(report.missing_in_db)}")
    click.echo(f"   Missing in enums: {len(report.missing_in_enum)}")
    click.echo(f"   Inconsistencies: {len(report.inconsistencies)}")

    # Show details
    if report.missing_in_db:
        click.echo(f"\n❌ Models in enum but missing in database:")
        for model in report.missing_in_db:
            click.echo(f"   - {model.model_id} ({model.provider})")

    if report.missing_in_enum:
        click.echo(f"\n⚠️  Models in database but not in enum:")
        for model in report.missing_in_enum[:10]:  # Limit to first 10
            click.echo(f"   - {model['name']} ({model['provider']})")
        if len(report.missing_in_enum) > 10:
            click.echo(f"   ... and {len(report.missing_in_enum) - 10} more")

    if report.inconsistencies:
        click.echo(f"\n⚠️  Inconsistencies found:")
        for issue in report.inconsistencies:
            click.echo(f"   - {issue}")

    # Overall status
    if report.missing_in_db or report.inconsistencies:
        click.echo(f"\n❌ Validation failed - inconsistencies found")
        return False
    else:
        click.echo(f"\n✅ Validation passed - enums and database are consistent")
        return True


def sync_enums_to_database(db_session: Session) -> bool:
    """Sync all enum models to database, ensuring they exist and are active."""
    click.echo("🔄 Syncing enums to database...")

    report = analyze_migration_gaps(db_session)

    # Add missing models
    added_count = migrate_enum_models_to_database(db_session, report)

    # Fix inconsistencies (activate inactive models that exist in enums)
    fixed_count = 0
    for enum_model in report.enum_models:
        db_model = (
            db_session.query(LLM)
            .filter(
                LLM.name == enum_model.model_id, LLM.provider == enum_model.provider
            )
            .first()
        )

        if db_model and not db_model.is_active:
            db_model.is_active = True
            fixed_count += 1

    if fixed_count > 0:
        try:
            db_session.commit()
            click.echo(f"✅ Activated {fixed_count} inactive models")
        except Exception as e:
            db_session.rollback()
            click.echo(f"❌ Error activating models: {e}")
            return False

    click.echo(f"✅ Sync completed: {added_count} added, {fixed_count} activated")
    return True


def generate_migration_report(
    db_session: Session, output_file: Optional[str] = None
) -> str:
    """Generate a detailed migration report."""
    report = analyze_migration_gaps(db_session)

    report_content = f"""
# LLM Database Migration Report
Generated: {datetime.utcnow().isoformat()}

## Summary
- Total enum models: {report.total_enum_models}
- Total database models: {report.total_db_models}
- Missing in database: {len(report.missing_in_db)}
- Missing in enums: {len(report.missing_in_enum)}
- Inconsistencies: {len(report.inconsistencies)}

## Enum Models
"""

    for model in report.enum_models:
        report_content += f"- {model.model_id} ({model.provider}) [{model.enum_name}]\n"

    if report.missing_in_db:
        report_content += f"\n## Missing in Database\n"
        for model in report.missing_in_db:
            report_content += f"- {model.model_id} ({model.provider})\n"

    if report.missing_in_enum:
        report_content += f"\n## Missing in Enums\n"
        for model in report.missing_in_enum:
            report_content += f"- {model['name']} ({model['provider']})\n"

    if report.inconsistencies:
        report_content += f"\n## Inconsistencies\n"
        for issue in report.inconsistencies:
            report_content += f"- {issue}\n"

    report_content += f"\n## Recommendations\n"

    if report.missing_in_db:
        report_content += (
            f"1. Run migration to add {len(report.missing_in_db)} missing models\n"
        )

    if report.missing_in_enum:
        report_content += f"2. Consider adding {len(report.missing_in_enum)} database models to enums if needed\n"

    if report.inconsistencies:
        report_content += f"3. Fix {len(report.inconsistencies)} consistency issues\n"

    if not (report.missing_in_db or report.missing_in_enum or report.inconsistencies):
        report_content += "✅ No issues found - enums and database are synchronized\n"

    if output_file:
        with open(output_file, "w") as f:
            f.write(report_content)
        click.echo(f"📄 Report saved to {output_file}")

    return report_content


@click.group()
def cli():
    """LLM data migration utilities for ensuring enum-database consistency."""
    pass


@cli.command()
@click.option("--force", is_flag=True, help="Force migration without confirmation")
def migrate(force):
    """Migrate enum models to database."""
    click.echo("🚀 Starting LLM data migration...")

    try:
        # Create database session
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()

        # Analyze current state
        report = analyze_migration_gaps(db_session)

        if not report.missing_in_db:
            click.echo("✅ No migration needed - all enum models exist in database")
            return

        click.echo(f"📋 Found {len(report.missing_in_db)} models to migrate:")
        for model in report.missing_in_db:
            click.echo(f"   - {model.model_id} ({model.provider})")

        if not force:
            if not click.confirm("Do you want to proceed with migration?"):
                click.echo("Migration cancelled.")
                return

        # Perform migration
        added_count = migrate_enum_models_to_database(db_session, report)

        if added_count > 0:
            click.echo(f"✅ Migration completed: {added_count} models added")
        else:
            click.echo("❌ Migration failed")

    except Exception as e:
        click.echo(f"❌ Migration error: {e}")
    finally:
        db_session.close()


@cli.command()
def validate():
    """Validate consistency between enums and database."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()

        is_valid = validate_database_enum_consistency(db_session)
        sys.exit(0 if is_valid else 1)

    except Exception as e:
        click.echo(f"❌ Validation error: {e}")
        sys.exit(1)
    finally:
        db_session.close()


@cli.command()
@click.option("--output", "-o", help="Output file for detailed report")
def analyze(output):
    """Analyze migration gaps and generate report."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()

        report_content = generate_migration_report(db_session, output)

        if not output:
            click.echo(report_content)

    except Exception as e:
        click.echo(f"❌ Analysis error: {e}")
    finally:
        db_session.close()


@cli.command()
@click.option("--force", is_flag=True, help="Force sync without confirmation")
def sync_enums(force):
    """Sync all enum models to database (migrate + fix inconsistencies)."""
    click.echo("🔄 Starting enum-database synchronization...")

    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()

        # Analyze first
        report = analyze_migration_gaps(db_session)
        changes_needed = len(report.missing_in_db) + len(report.inconsistencies)

        if changes_needed == 0:
            click.echo(
                "✅ No synchronization needed - enums and database are already consistent"
            )
            return

        click.echo(f"📋 Synchronization will make {changes_needed} changes")

        if not force:
            if not click.confirm("Do you want to proceed with synchronization?"):
                click.echo("Synchronization cancelled.")
                return

        # Perform sync
        success = sync_enums_to_database(db_session)

        if success:
            click.echo("✅ Synchronization completed successfully")
        else:
            click.echo("❌ Synchronization failed")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Synchronization error: {e}")
        sys.exit(1)
    finally:
        db_session.close()


if __name__ == "__main__":
    cli()
