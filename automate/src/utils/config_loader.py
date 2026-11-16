"""Configuration loader for the automation."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel
from functools import lru_cache


class Settings(BaseModel):
    """Main settings model."""

    # General
    project_name: str = "Averta Lead Generation"
    version: str = "1.0.0"
    timezone: str = "America/Sao_Paulo"
    language: str = "pt-BR"
    mode: str = "full"

    # Paths
    data_dir: str = "data"
    queries_dir: str = "queries/generated"
    output_dir: str = "output"
    logs_dir: str = "logs"
    cache_dir: str = "data/cache"
    master_db: str = "data/master.db"

    # Scraper
    scraper_execution_mode: str = "binary"
    scraper_binary_path: str = "./google-maps-scraper"
    scraper_rest_api_base_url: str = "http://localhost:8080"
    scraper_rest_api_timeout_seconds: int = 300
    scraper_docker_image: str = "gosom/google-maps-scraper:latest"
    scraper_params_depth: int = 2
    scraper_params_concurrency: int = 4
    scraper_params_fast_mode: bool = False
    scraper_params_extract_emails: bool = True
    scraper_params_extra_reviews: bool = False
    scraper_params_exit_on_inactivity: str = "5m"
    scraper_params_grid_cell_km: int = 10
    scraper_limits_max_results_per_query: int = 500
    scraper_limits_max_queries_per_run: int = 200
    scraper_limits_max_total_results: int = 50000
    scraper_limits_rate_limit_per_minute: int = 30
    scraper_output_format: str = "json"

    # Qualification
    qual_weights_operational_fit: float = 0.40
    qual_weights_commercial_fit: float = 0.35
    qual_weights_data_confidence: float = 0.25
    qual_thresholds_A_min: int = 85
    qual_thresholds_B_min: int = 70
    qual_thresholds_C_min: int = 50

    # Export
    export_format: str = "xlsx"
    export_leads_ab: str = "output/leads_A_B.xlsx"
    export_leads_c: str = "output/leads_C.xlsx"
    export_daily_report: str = "output/reports/daily_{date}.xlsx"
    export_whatsapp_ready: str = "output/whatsapp_ready/leads_whatsapp_{date}.xlsx"
    export_coverage_report: str = "output/reports/coverage_{date}.xlsx"
    export_decision_makers_report: str = "output/reports/decision_makers_{date}.xlsx"

    # Logging
    logging_level: str = "INFO"
    logging_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    logging_rotation: str = "10 MB"
    logging_retention: str = "30 days"
    logging_compression: str = "zip"
    logging_file: str = "logs/automation.log"
    logging_console: bool = True

    # Performance
    perf_batch_size_queries: int = 50
    perf_batch_size_scrape: int = 100
    perf_batch_size_qualify: int = 500
    perf_batch_size_export: int = 1000
    perf_max_workers_scraper: int = 4
    perf_max_workers_qualification: int = 8
    perf_max_workers_enrichment: int = 4
    perf_scraper_timeout_seconds: int = 300
    perf_enrichment_timeout_seconds: int = 60
    perf_api_timeout_seconds: int = 30
    perf_max_retries: int = 3
    perf_retry_delay_seconds: int = 5
    perf_retry_backoff_factor: float = 2.0

    # WhatsApp
    whatsapp_enabled: bool = False
    whatsapp_api_version: str = "v18.0"
    whatsapp_business_account_id: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_access_token: str = ""
    whatsapp_webhook_verify_token: str = ""
    whatsapp_sending_rate_limit_per_minute: int = 20
    whatsapp_opt_in_required: bool = True
    whatsapp_business_hours_only: bool = True
    whatsapp_business_hours_start: str = "08:00"
    whatsapp_business_hours_end: str = "18:00"
    whatsapp_timezone: str = "America/Sao_Paulo"

    # Email
    email_enabled: bool = False
    email_provider: str = "smtp"
    smtp_host: str = "smtppro.zoho.com"
    smtp_port: int = 465
    smtp_user: str = "pedrolarrieuceo@avertabrasil.com.br"
    smtp_password: str = ""
    smtp_from_email: str = "contato@avertabrasil.com.br"
    smtp_from_name: str = "Averta Logística Inteligente"
    smtp_use_tls: bool = False
    smtp_use_ssl: bool = True
    smtp_timeout: int = 30
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@averta.com"
    sendgrid_from_name: str = "Averta Logística"
    email_campaigns_default_name: str = "Prospecção Ativa Averta - Email"
    email_campaigns_default_description: str = "Prospecção de leads A e B qualificados via email"
    email_campaigns_default_lead_classifications: List[str] = ["A", "B"]
    email_campaigns_default_min_score: float = 70
    email_campaigns_default_max_emails_per_lead: int = 4
    email_campaigns_default_business_hours_only: bool = True
    email_campaigns_default_business_hours_start: int = 8
    email_campaigns_default_business_hours_end: int = 18
    email_campaigns_default_timezone: str = "America/Sao_Paulo"
    email_campaigns_default_rate_limit_per_minute: int = 10
    email_campaigns_default_rate_limit_per_hour: int = 200
    email_campaigns_default_rate_limit_per_day: int = 1000


@lru_cache(maxsize=1)
def load_settings(config_path: Optional[str] = None) -> Settings:
    """Load settings from YAML config file."""
    if config_path is None:
        # Find config file relative to this file
        base_dir = Path(__file__).parent.parent.parent
        config_path = base_dir / "config" / "settings.yaml"

    config_path = Path(config_path)

    if not config_path.exists():
        # Return default settings if config file doesn't exist
        return Settings()

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    # Flatten nested config for Pydantic
    flat_config = {}

    def flatten_dict(d: Dict, prefix: str = "") -> Dict:
        result = {}
        for k, v in d.items():
            new_key = f"{prefix}{k}" if prefix else k
            if isinstance(v, dict):
                result.update(flatten_dict(v, f"{new_key}_"))
            else:
                result[new_key] = v
        return result

    flat_config = flatten_dict(config_data)

    # Map to Settings fields
    settings_dict = {}
    field_mapping = {
        'general_project_name': 'project_name',
        'general_version': 'version',
        'general_timezone': 'timezone',
        'general_language': 'language',
        'general_mode': 'mode',
        'general_paths_data_dir': 'data_dir',
        'general_paths_queries_dir': 'queries_dir',
        'general_paths_output_dir': 'output_dir',
        'general_paths_logs_dir': 'logs_dir',
        'general_paths_cache_dir': 'cache_dir',
        'general_paths_master_db': 'master_db',
        'scraper_execution_mode': 'scraper_execution_mode',
        'scraper_binary_path': 'scraper_binary_path',
        'scraper_rest_api_base_url': 'scraper_rest_api_base_url',
        'scraper_rest_api_timeout_seconds': 'scraper_rest_api_timeout_seconds',
        'scraper_docker_image': 'scraper_docker_image',
        'scraper_params_depth': 'scraper_params_depth',
        'scraper_params_concurrency': 'scraper_params_concurrency',
        'scraper_params_fast_mode': 'scraper_params_fast_mode',
        'scraper_params_extract_emails': 'scraper_params_extract_emails',
        'scraper_params_extra_reviews': 'scraper_params_extra_reviews',
        'scraper_params_exit_on_inactivity': 'scraper_params_exit_on_inactivity',
        'scraper_params_grid_cell_km': 'scraper_params_grid_cell_km',
        'scraper_limits_max_results_per_query': 'scraper_limits_max_results_per_query',
        'scraper_limits_max_queries_per_run': 'scraper_limits_max_queries_per_run',
        'scraper_limits_max_total_results': 'scraper_limits_max_total_results',
        'scraper_limits_rate_limit_per_minute': 'scraper_limits_rate_limit_per_minute',
        'scraper_output_format': 'scraper_output_format',
        'qualification_weights_operational_fit': 'qual_weights_operational_fit',
        'qualification_weights_commercial_fit': 'qual_weights_commercial_fit',
        'qualification_weights_data_confidence': 'qual_weights_data_confidence',
        'qualification_thresholds_A_min': 'qual_thresholds_A_min',
        'qualification_thresholds_B_min': 'qual_thresholds_B_min',
        'qualification_thresholds_C_min': 'qual_thresholds_C_min',
        'export_format': 'export_format',
        'export_files_leads_ab': 'export_leads_ab',
        'export_files_leads_c': 'export_leads_c',
        'export_files_daily_report': 'export_daily_report',
        'export_files_whatsapp_ready': 'export_whatsapp_ready',
        'export_files_coverage_report': 'export_coverage_report',
        'export_files_decision_makers_report': 'export_decision_makers_report',
        'logging_level': 'logging_level',
        'logging_format': 'logging_format',
        'logging_rotation': 'logging_rotation',
        'logging_retention': 'logging_retention',
        'logging_compression': 'logging_compression',
        'logging_file': 'logging_file',
        'logging_console': 'logging_console',
        'performance_batch_size_queries': 'perf_batch_size_queries',
        'performance_batch_size_scrape': 'perf_batch_size_scrape',
        'performance_batch_size_qualify': 'perf_batch_size_qualify',
        'performance_batch_size_export': 'perf_batch_size_export',
        'performance_max_workers_scraper': 'perf_max_workers_scraper',
        'performance_max_workers_qualification': 'perf_max_workers_qualification',
        'performance_max_workers_enrichment': 'perf_max_workers_enrichment',
        'performance_scraper_timeout_seconds': 'perf_scraper_timeout_seconds',
        'performance_enrichment_timeout_seconds': 'perf_enrichment_timeout_seconds',
        'performance_api_timeout_seconds': 'perf_api_timeout_seconds',
        'performance_max_retries': 'perf_max_retries',
        'performance_retry_delay_seconds': 'perf_retry_delay_seconds',
        'performance_retry_backoff_factor': 'perf_retry_backoff_factor',
        'whatsapp_enabled': 'whatsapp_enabled',
        'whatsapp_api_version': 'whatsapp_api_version',
        'whatsapp_business_account_id': 'whatsapp_business_account_id',
        'whatsapp_phone_number_id': 'whatsapp_phone_number_id',
        'whatsapp_access_token': 'whatsapp_access_token',
        'whatsapp_webhook_verify_token': 'whatsapp_webhook_verify_token',
        'whatsapp_sending_rate_limit_per_minute': 'whatsapp_sending_rate_limit_per_minute',
        'whatsapp_opt_in_required': 'whatsapp_opt_in_required',
        'whatsapp_business_hours_only': 'whatsapp_business_hours_only',
        'whatsapp_business_hours_start': 'whatsapp_business_hours_start',
        'whatsapp_business_hours_end': 'whatsapp_business_hours_end',
        'whatsapp_timezone': 'whatsapp_timezone',

        # Email
        'email_enabled': 'email_enabled',
        'email_provider': 'email_provider',
        'email_smtp_host': 'smtp_host',
        'email_smtp_port': 'smtp_port',
        'email_smtp_user': 'smtp_user',
        'email_smtp_password': 'smtp_password',
        'email_smtp_from_email': 'smtp_from_email',
        'email_smtp_from_name': 'smtp_from_name',
        'email_smtp_use_tls': 'smtp_use_tls',
        'email_smtp_use_ssl': 'smtp_use_ssl',
        'email_smtp_timeout': 'smtp_timeout',
        'email_sendgrid_api_key': 'sendgrid_api_key',
        'email_sendgrid_from_email': 'sendgrid_from_email',
        'email_sendgrid_from_name': 'sendgrid_from_name',
        'email_campaigns_default_name': 'email_campaigns_default_name',
        'email_campaigns_default_description': 'email_campaigns_default_description',
        'email_campaigns_default_lead_classifications': 'email_campaigns_default_lead_classifications',
        'email_campaigns_default_min_score': 'email_campaigns_default_min_score',
        'email_campaigns_default_max_emails_per_lead': 'email_campaigns_default_max_emails_per_lead',
        'email_campaigns_default_business_hours_only': 'email_campaigns_default_business_hours_only',
        'email_campaigns_default_business_hours_start': 'email_campaigns_default_business_hours_start',
        'email_campaigns_default_business_hours_end': 'email_campaigns_default_business_hours_end',
        'email_campaigns_default_timezone': 'email_campaigns_default_timezone',
        'email_campaigns_default_rate_limit_per_minute': 'email_campaigns_default_rate_limit_per_minute',
        'email_campaigns_default_rate_limit_per_hour': 'email_campaigns_default_rate_limit_per_hour',
        'email_campaigns_default_rate_limit_per_day': 'email_campaigns_default_rate_limit_per_day',
    }

    for yaml_key, settings_key in field_mapping.items():
        if yaml_key in flat_config:
            settings_dict[settings_key] = flat_config[yaml_key]

    return Settings(**settings_dict)


def get_settings() -> Settings:
    """Get settings instance (cached)."""
    return load_settings()


def reload_settings(config_path: Optional[str] = None) -> Settings:
    """Force reload settings from config file."""
    load_settings.cache_clear()
    return load_settings(config_path)