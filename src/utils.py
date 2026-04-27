"""
Utility Functions Module
Common helper functions used across the pipeline
"""
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar
from datetime import datetime, timedelta

T = TypeVar('T')

def generate_hash(content: str) -> str:
    """Generate MD5 hash of content"""
    return hashlib.md5(content.encode()).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem"""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # Remove control characters
    filename = ''.join(c for c in filename if ord(c) > 31)
    return filename.strip()

def ensure_dir(path: Path) -> Path:
    """Ensure directory exists"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        raise OSError(f"Failed to create directory {path}: {e}")

def save_json(data: Any, file_path: Path, indent: int = 2):
    """Save data to JSON file with error handling"""
    try:
        ensure_dir(file_path.parent)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
    except Exception as e:
        raise IOError(f"Failed to save JSON to {file_path}: {e}")

def load_json(file_path: Path) -> Any:
    """Load data from JSON file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise IOError(f"Failed to load JSON from {file_path}: {e}")

def format_duration(seconds: float) -> str:
    """Format duration in human-readable form"""
    if seconds < 0:
        return "0.00s"
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"

def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable form"""
    if bytes_size < 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"

def extract_article_numbers(text: str) -> List[int]:
    """Extract article numbers from text (e.g., 'Art. 123')"""
    pattern = r'Art\.\s*(\d+)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return [int(m) for m in matches]

def extract_equations(latex_text: str) -> List[str]:
    """Extract LaTeX equations from text"""
    equations = []
    
    # Display math: $$...$$
    display_pattern = r'\$\$(.*?)\$\$'
    equations.extend(re.findall(display_pattern, latex_text, re.DOTALL))
    
    # Inline math: $...$
    inline_pattern = r'\$(.*?)\$'
    equations.extend(re.findall(inline_pattern, latex_text))
    
    return equations

def clean_latex(latex: str) -> str:
    """Clean LaTeX string for processing"""
    if not latex:
        return ""
    # Remove comments
    latex = re.sub(r'%.*', '', latex)
    # Remove extra whitespace
    latex = ' '.join(latex.split())
    return latex.strip()

def create_python_package_structure(base_dir: Path, package_name: str):
    """Create Python package directory structure"""
    package_dir = base_dir / package_name
    # Create directories
    ensure_dir(package_dir)
    ensure_dir(package_dir / 'tests')
    
    # Create __init__.py files
    (package_dir / '__init__.py').touch(exist_ok=True)
    (package_dir / 'tests' / '__init__.py').touch(exist_ok=True)
    
    return package_dir

def generate_module_docstring(
    module_name: str,
    description: str,
    author: str = "Maxwell Pipeline",
    created: Optional[datetime] = None
) -> str:
    """Generate Python module docstring"""
    if created is None:
        created = datetime.now()
    docstring = f'''"""
{module_name}
{description}
Author: {author}
Created: {created.strftime("%Y-%m-%d")}
"""'''
    return docstring

def generate_function_signature(
    func_name: str,
    params: List[Dict[str, str]],
    return_type: str = "None"
) -> str:
    """Generate Python function signature with type hints"""
    param_strs = []
    for param in params:
        param_str = f"{param['name']}: {param['type']}"
        if 'default' in param:
            param_str += f" = {param['default']}"
        param_strs.append(param_str)
    params_str = ", ".join(param_strs)
    return f"def {func_name}({params_str}) -> {return_type}:"

def wrap_in_try_except(code: str, exception_handling: str = "pass") -> str:
    """Wrap code block in try-except"""
    lines = code.split('\n')
    indented_code = '\n    '.join(lines)
    wrapped = f"""try:
    {indented_code}
except Exception as e:
    {exception_handling}"""
    return wrapped

def estimate_processing_time(
    total_items: int,
    items_processed: int,
    elapsed_seconds: float
) -> float:
    """Estimate remaining processing time"""
    if total_items <= 0 or items_processed <= 0 or elapsed_seconds <= 0:
        return 0.0
    if items_processed >= total_items:
        return 0.0
    
    rate = elapsed_seconds / items_processed
    remaining_items = total_items - items_processed
    return max(0.0, remaining_items * rate)

def create_progress_bar_dict(
    current: int,
    total: int,
    description: str = ""
) -> Dict[str, Any]:
    """Create progress information dictionary"""
    if total <= 0:
        percentage = 0.0
    else:
        percentage = min(100.0, max(0.0, (current / total * 100)))
    
    return {
        'current': current,
        'total': total,
        'percentage': percentage,
        'description': description,
        'completed': current >= total
    }

def validate_api_key(api_key: str, min_length: int = 20) -> bool:
    """Validate API key format"""
    if not api_key or len(api_key) < min_length:
        return False
    
    # Check for placeholder values
    placeholders = ['your-', 'example', 'test', 'dummy', 'enter-your', 'xxxxx']
    if any(p in api_key.lower() for p in placeholders):
        return False
    
    # Check for obvious patterns
    if all(c == api_key[0] for c in api_key):
        return False
    
    return True

def retry_with_backoff(
    func,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Retry function with exponential backoff"""
    delay = initial_delay
    
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            if attempt == max_attempts - 1:
                raise
            
            time.sleep(delay)
            delay *= backoff_factor

def merge_dicts_deep(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_deep(result[key], value)
        else:
            result[key] = value
    
    return result

def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split list into chunks"""
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_list(nested_list: List[List[T]]) -> List[T]:
    """Flatten nested list"""
    return [item for sublist in nested_list for item in sublist]

def get_file_size(path: Path) -> int:
    """Get file size in bytes with error handling"""
    try:
        return path.stat().st_size
    except Exception as e:
        raise OSError(f"Failed to get file size for {path}: {e}")

def check_disk_space(path: Path, required_bytes: int) -> bool:
    """Check if there's enough disk space available"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(path.parent)
        return free >= required_bytes
    except Exception as e:
        raise OSError(f"Failed to check disk space for {path}: {e}")

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for logging"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def parse_page_range(page_range_str: str) -> List[int]:
    """Parse page range string like '1-5,10,15-20' into list of page numbers"""
    pages = set()
    ranges = page_range_str.split(',')
    
    for r in ranges:
        r = r.strip()
        if not r:
            continue
        
        if '-' in r:
            start_str, end_str = r.split('-')
            try:
                start = int(start_str.strip())
                end = int(end_str.strip())
                pages.update(range(min(start, end), max(start, end) + 1))
            except ValueError:
                continue
        else:
            try:
                pages.add(int(r.strip()))
            except ValueError:
                continue
    
    return sorted(pages)

class Timer:
    """Context manager for timing code blocks"""
    def __init__(self, name: str = "Operation", logger=None):
        self.name = name
        self.logger = logger
        self.start_time = None
        self.end_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        
        msg = f"{self.name} took {format_duration(self.elapsed)}"
        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)
    
    def get_elapsed(self) -> float:
        """Get elapsed time in seconds"""
        return self.elapsed if self.elapsed is not None else 0.0

def measure_execution_time(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"{func.__name__} took {format_duration(elapsed)}")
        return result
    return wrapper

def normalize_path(path: Union[str, Path]) -> Path:
    """Normalize and resolve path"""
    return Path(path).expanduser().resolve()

def is_valid_pdf_path(path: Path) -> bool:
    """Check if path is a valid PDF file"""
    return path.exists() and path.is_file() and path.suffix.lower() == '.pdf'

def calculate_checksum(file_path: Path, algorithm: str = 'md5') -> str:
    """Calculate file checksum using specified algorithm"""
    hash_func = getattr(hashlib, algorithm.lower())()
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        raise IOError(f"Failed to calculate checksum for {file_path}: {e}")

def human_readable_memory(bytes_size: int) -> str:
    """Convert bytes to human readable memory format"""
    return format_file_size(bytes_size)

def get_system_info() -> Dict[str, Any]:
    """Get basic system information"""
    import platform
    import psutil
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'total_memory_gb': psutil.virtual_memory().total / (1024**3),
        'available_disk_space_gb': psutil.disk_usage('/').free / (1024**3)
    }

if __name__ == '__main__':
    # Test utilities
    print("Testing utilities...")
    # Test hash generation
    test_hash = generate_hash("test content")
    print(f"Hash: {test_hash}")
    
    # Test article extraction
    text = "This is Art. 123 and Art. 456"
    articles = extract_article_numbers(text)
    print(f"Articles found: {articles}")
    
    # Test duration formatting
    print(f"Duration: {format_duration(3665)}")
    
    # Test timer
    with Timer("Test operation"):
        time.sleep(0.1)
    
    # Test page range parsing
    pages = parse_page_range("1-5,10,15-20")
    print(f"Parsed pages: {pages}")
    
    # Test API key validation
    print(f"Valid API key: {validate_api_key('my_secret_key_12345')}")
    print(f"Invalid API key: {validate_api_key('your-api-key-here')}")
    
    print("All utilities tests passed!")