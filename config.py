"""
Configurações centralizadas do sistema de verificação de WAF
"""

import os
from typing import Dict, List

# Configurações de WAF
WAF_PATTERNS = {
    'cloudflare': [
        'cloudflare', '__cfduid', 'cf-ray', 'cf-cache-status',
        'x-cache-status', 'cf-request-id'
    ],
    'aws_waf': [
        'x-amz-cf-id', 'x-amz-cf-pop', 'x-amz-cf-id',
        'x-amz-waf-id', 'x-amz-waf-pop'
    ],
    'akamai': [
        'akamai', 'x-akamai-transformed', 'x-akamai-origin-hop',
        'x-akamai-ssl', 'x-akamai-ssl-client'
    ],
    'fastly': [
        'fastly', 'x-fastly', 'x-fastly-ssl', 'x-fastly-ssl-client'
    ],
    'imperva': [
        'incap_ses', 'visid_incap', 'x-iinfo', 'x-cdn',
        'incap_visid_83', 'incap_ses_83'
    ],
    'f5_bigip': [
        'bigip', 'x-wa-info', 'x-asg', 'x-asg-info',
        'x-bigip', 'x-bigip-*'
    ],
    'barracuda': [
        'barra_counter_session', 'barra_counter_session',
        'x-barra', 'x-barracuda'
    ],
    'citrix': [
        'citrix', 'ns_af', 'x-citrix', 'x-netscaler'
    ],
    'sucuri': [
        'sucuri', 'x-sucuri', 'x-sucuri-*', 'sucuri-*'
    ],
    'cloudfront': [
        'x-amz-cf-id', 'x-amz-cf-pop', 'x-amz-cf-id',
        'x-cache', 'x-cache-lookup'
    ],
    'incapsula': [
        'incap_ses', 'visid_incap', 'x-iinfo',
        'incap_visid', 'incap_ses'
    ],
    'maxcdn': [
        'x-cdn', 'x-cdn-pop', 'x-cdn-ssl'
    ],
    'keycdn': [
        'x-cdn', 'x-cdn-pop', 'x-cdn-ssl'
    ]
}

# Headers HTTP para simular navegador real
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'DNT': '1'
}

# Configurações de timeout e retry
HTTP_TIMEOUT = 10
HTTP_RETRY_ATTEMPTS = 3
HTTP_RETRY_DELAY = 1

# Configurações de paginação Route53
ROUTE53_PAGE_SIZE = 100
ROUTE53_MAX_PAGES = 1000

# Configurações de saída
OUTPUT_DIR = 'output'
INPUT_DIR = 'input'
CSV_ENCODING = 'utf-8'
JSON_INDENT = 2

# Configurações de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Configurações de rate limiting
RATE_LIMIT_DELAY = 0.5  # segundos entre requisições
MAX_CONCURRENT_REQUESTS = 5

# Configurações de detecção
DNS_CHECK_ENABLED = True
HTTP_CHECK_ENABLED = True
COOKIE_CHECK_ENABLED = True
BODY_CHECK_ENABLED = True

# Configurações de S3
S3_UPLOAD_TIMEOUT = 30
S3_MAX_RETRIES = 3

# Configurações de segurança
VERIFY_SSL = False  # Pode ser configurado via variável de ambiente
ALLOW_REDIRECTS = True
MAX_REDIRECTS = 5

def get_config() -> Dict:
    """Retorna configuração completa do sistema"""
    return {
        'waf_patterns': WAF_PATTERNS,
        'browser_headers': BROWSER_HEADERS,
        'http_timeout': HTTP_TIMEOUT,
        'http_retry_attempts': HTTP_RETRY_ATTEMPTS,
        'http_retry_delay': HTTP_RETRY_DELAY,
        'route53_page_size': ROUTE53_PAGE_SIZE,
        'route53_max_pages': ROUTE53_MAX_PAGES,
        'output_dir': OUTPUT_DIR,
        'input_dir': INPUT_DIR,
        'csv_encoding': CSV_ENCODING,
        'json_indent': JSON_INDENT,
        'log_level': LOG_LEVEL,
        'log_format': LOG_FORMAT,
        'log_date_format': LOG_DATE_FORMAT,
        'rate_limit_delay': RATE_LIMIT_DELAY,
        'max_concurrent_requests': MAX_CONCURRENT_REQUESTS,
        'dns_check_enabled': DNS_CHECK_ENABLED,
        'http_check_enabled': HTTP_CHECK_ENABLED,
        'cookie_check_enabled': COOKIE_CHECK_ENABLED,
        'body_check_enabled': BODY_CHECK_ENABLED,
        's3_upload_timeout': S3_UPLOAD_TIMEOUT,
        's3_max_retries': S3_MAX_RETRIES,
        'verify_ssl': os.getenv('VERIFY_SSL', str(VERIFY_SSL)).lower() == 'true',
        'allow_redirects': ALLOW_REDIRECTS,
        'max_redirects': MAX_REDIRECTS
    }

def get_waf_patterns() -> Dict[str, List[str]]:
    """Retorna padrões de WAF configurados"""
    return WAF_PATTERNS

def get_browser_headers() -> Dict[str, str]:
    """Retorna headers de navegador configurados"""
    return BROWSER_HEADERS.copy()

def is_dns_check_enabled() -> bool:
    """Verifica se verificação DNS está habilitada"""
    return DNS_CHECK_ENABLED

def is_http_check_enabled() -> bool:
    """Verifica se verificação HTTP está habilitada"""
    return HTTP_CHECK_ENABLED

def is_cookie_check_enabled() -> bool:
    """Verifica se verificação de cookies está habilitada"""
    return COOKIE_CHECK_ENABLED

def is_body_check_enabled() -> bool:
    """Verifica se verificação de corpo está habilitada"""
    return BODY_CHECK_ENABLED
