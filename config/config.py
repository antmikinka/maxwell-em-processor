"""
Configuration Management Module
Handles environment variables, paths, and application settings
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings from environment variables"""
    # Mathpix API Configuration
    mathpix_app_id: str = Field(..., env='MATHPIX_APP_ID')
    mathpix_app_key: str = Field(..., env='MATHPIX_APP_KEY')
    mathpix_url: str = Field(default='https://api.mathpix.com', env='MATHPIX_URL')
    
    # Logging Configuration
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    enable_api_caching: bool = Field(default=True, env='ENABLE_API_CACHING')
    enable_checkpoints: bool = Field(default=True, env='ENABLE_CHECKPOINTS')
    
    # Processing Configuration
    max_concurrent_requests: int = Field(default=3, env='MAX_CONCURRENT_REQUESTS')
    timeout_seconds: int = Field(default=600, env='TIMEOUT_SECONDS')  # Increased for large PDFs
    retry_attempts: int = Field(default=5, env='RETRY_ATTEMPTS')
    retry_delay_seconds: int = Field(default=10, env='RETRY_DELAY_SECONDS')
    
    # Output Paths
    input_dir: str = Field(default='input', env='INPUT_DIR')
    output_dir: str = Field(default='output', env='OUTPUT_DIR')
    cache_dir: str = Field(default='output/cache', env='CACHE_DIR')
    logs_dir: str = Field(default='output/logs', env='LOGS_DIR')
    checkpoints_dir: str = Field(default='output/checkpoints', env='CHECKPOINTS_DIR')
    
    # Mathpix-specific settings
    max_file_size_mb: int = Field(default=100, env='MAX_FILE_SIZE_MB')  # Mathpix limit
    large_pdf_chunk_size: int = Field(default=50, env='LARGE_PDF_CHUNK_SIZE')  # Pages per chunk
    
    # Feature Flags
    improve_mathpix: bool = Field(default=False, env='IMPROVE_MATHPIX')
    enable_quantum_packages: bool = Field(default=True, env='ENABLE_QUANTUM_PACKAGES')
    generate_visualizations: bool = Field(default=True, env='GENERATE_VISUALIZATIONS')
    generate_tests: bool = Field(default=True, env='GENERATE_TESTS')

    # Simplified Mode Configuration
    simple_mode: bool = Field(default=False, env='SIMPLE_MODE')  # NEW: Mathpix-only mode
    mathpix_extract_all_formats: bool = Field(default=True, env='MATHPIX_EXTRACT_ALL_FORMATS')
    preserve_all_metadata: bool = Field(default=True, env='PRESERVE_ALL_METADATA')

    # Quality Control Configuration
    confidence_threshold: float = Field(default=0.85, env='CONFIDENCE_THRESHOLD')  # Minimum confidence for acceptance
    enable_quality_control: bool = Field(default=True, env='ENABLE_QUALITY_CONTROL')  # Enable confidence-based filtering
    quality_check_enabled: bool = Field(default=True, env='QUALITY_CHECK_ENABLED')  # Quality verification passes

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False

class PathManager:
    """Manages all project paths and ensures directories exist"""
    def __init__(self, settings: Settings):
        self.settings = settings
        self.project_root = Path(__file__).parent.parent
        # Define all paths
        self.input_dir = self.project_root / settings.input_dir
        self.output_dir = self.project_root / settings.output_dir
        self.cache_dir = self.project_root / settings.cache_dir
        self.logs_dir = self.project_root / settings.logs_dir
        self.checkpoints_dir = self.project_root / settings.checkpoints_dir
        
        # Output subdirectories
        self.raw_ocr_dir = self.output_dir / 'raw_ocr'
        self.organized_dir = self.output_dir / 'organized'
        self.database_dir = self.output_dir / 'database'
        self.generated_code_dir = self.output_dir / 'generated_code'
        
        # Cache subdirectories
        self.mathpix_cache_dir = self.cache_dir / 'mathpix'
        self.toc_cache_dir = self.cache_dir / 'toc'
        
        # Config directory
        self.config_dir = self.project_root / 'config'
        
        # Create all directories
        self._create_directories()

    def _create_directories(self):
        """Create all necessary directories"""
        directories = [
            self.input_dir,
            self.output_dir,
            self.cache_dir,
            self.logs_dir,
            self.checkpoints_dir,
            self.raw_ocr_dir,
            self.organized_dir,
            self.database_dir,
            self.generated_code_dir,
            self.mathpix_cache_dir,
            self.toc_cache_dir,  # Added TOC cache directory
            self.config_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_volume_dir(self, volume_num: int, subdir: str = 'raw_ocr') -> Path:
        """Get directory for specific volume"""
        base_dir = getattr(self, f'{subdir}_dir')
        volume_dir = base_dir / f'volume_{volume_num}'
        volume_dir.mkdir(parents=True, exist_ok=True)
        return volume_dir

    def get_toc_file(self, volume_num: int) -> Path:
        """Get path to TOC data file for specific volume"""
        return self.database_dir / f'volume_{volume_num}_toc.json'

    def get_general_toc_file(self) -> Path:
        """Get path to general TOC data file for all volumes"""
        return self.database_dir / 'general_toc.json'

    def get_checkpoint_file(self, step: str) -> Path:
        """Get checkpoint file for specific step"""
        return self.checkpoints_dir / f'{step}.json'

    def get_log_file(self, log_name: str) -> Path:
        """Get path to specific log file"""
        return self.logs_dir / f'{log_name}.log'

# Global settings instance
try:
    settings = Settings()
    paths = PathManager(settings)
except Exception as e:
    print(f"Error loading configuration: {e}")
    print("Please ensure .env file exists and contains all required values.")
    print("Copy .env.example to .env and fill in your API credentials.")
    raise

def get_settings() -> Settings:
    """Get global settings instance"""
    return settings

def get_paths() -> PathManager:
    """Get global paths instance"""
    return paths

if __name__ == '__main__':
    # Test configuration
    print("Configuration loaded successfully!")
    print(f"Project root: {paths.project_root}")
    print(f"Output directory: {paths.output_dir}")
    print(f"Log level: {settings.log_level}")
    print(f"Mathpix URL: {settings.mathpix_url}")
    print(f"Timeout: {settings.timeout_seconds}s")
    print(f"Max file size: {settings.max_file_size_mb}MB")