#!/usr/bin/env python3
"""
Sistema de Verificação de WAF
Verifica se URLs estão protegidas por WAF através de análise de DNS e requisições HTTP
"""

import os
import sys
import json
import csv
import time
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import click
import boto3
import requests
import dns.resolver
from botocore.exceptions import ClientError, NoCredentialsError
import pandas as pd
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WAFChecker:
    """Classe principal para verificação de WAF"""
    
    def __init__(self, local_mode: bool = False, s3_bucket: Optional[str] = None):
        self.local_mode = local_mode
        self.s3_bucket = s3_bucket
        self.session = boto3.Session()
        
        # Headers para simular navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Padrões conhecidos de WAF
        self.waf_patterns = {
            'cloudflare': ['cloudflare', '__cfduid', 'cf-ray'],
            'aws_waf': ['x-amz-cf-id', 'x-amz-cf-pop', 'x-amz-cf-id'],
            'akamai': ['akamai', 'x-akamai-transformed'],
            'fastly': ['fastly', 'x-fastly'],
            'imperva': ['incap_ses', 'visid_incap', 'x-iinfo'],
            'f5_bigip': ['bigip', 'x-wa-info'],
            'barracuda': ['barra_counter_session', 'barra_counter_session'],
            'citrix': ['citrix', 'ns_af'],
            'sucuri': ['sucuri', 'x-sucuri'],
            'cloudfront': ['x-amz-cf-id', 'x-amz-cf-pop'],
        }
    
    def get_route53_records(self, hosted_zone_id: Optional[str] = None, max_records: Optional[int] = None) -> List[str]:
        """Lista registros DNS do Route53 com paginação"""
        urls = []
        
        try:
            route53 = self.session.client('route53')
            
            # Se não especificar hosted zone, lista todas
            if hosted_zone_id:
                zones = [{'Id': hosted_zone_id}]
            else:
                zones = route53.list_hosted_zones()['HostedZones']
            
            for zone in zones:
                logger.info(f"Processando zona hospedada: {zone['Name']}")
                
                paginator = route53.get_paginator('list_resource_record_sets')
                page_iterator = paginator.paginate(HostedZoneId=zone['Id'])
                
                record_count = 0
                for page in page_iterator:
                    for record in page['ResourceRecordSets']:
                        if record['Type'] in ['A', 'CNAME', 'AAAA']:
                            # Construir URL
                            if record['Type'] == 'CNAME':
                                domain = record['Name'].rstrip('.')
                            else:
                                domain = record['Name'].rstrip('.')
                            
                            # Adicionar protocolo se não existir
                            if not domain.startswith(('http://', 'https://')):
                                url = f"https://{domain}"
                            else:
                                url = domain
                            
                            urls.append(url)
                            record_count += 1
                            
                            # Verificar limite
                            if max_records and record_count >= max_records:
                                logger.info(f"Limite de {max_records} registros atingido")
                                return urls
                
                logger.info(f"Total de registros processados na zona {zone['Name']}: {record_count}")
        
        except NoCredentialsError:
            logger.error("Credenciais AWS não encontradas")
            raise
        except ClientError as e:
            logger.error(f"Erro ao acessar Route53: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise
        
        return urls
    
    def load_urls_from_file(self, file_path: str, max_urls: Optional[int] = None) -> List[str]:
        """Carrega URLs de um arquivo local"""
        urls = []
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Adicionar protocolo se não existir
                        if not line.startswith(('http://', 'https://')):
                            line = f"https://{line}"
                        urls.append(line)
                        
                        if max_urls and len(urls) >= max_urls:
                            break
            
            logger.info(f"Carregadas {len(urls)} URLs do arquivo {file_path}")
            return urls
            
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            raise
    
    def check_waf_protection(self, url: str) -> Dict[str, any]:
        """Verifica se uma URL está protegida por WAF"""
        result = {
            'url': url,
            'waf_detected': False,
            'waf_type': None,
            'waf_indicators': [],
            'status_code': None,
            'response_time': None,
            'error': None
        }
        
        try:
            # Verificar DNS primeiro
            domain = urlparse(url).netloc
            dns_indicators = self._check_dns_indicators(domain)
            if dns_indicators:
                result['waf_detected'] = True
                result['waf_indicators'].extend(dns_indicators)
            
            # Fazer requisição HTTP
            start_time = time.time()
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=10, 
                allow_redirects=True,
                verify=False
            )
            result['response_time'] = time.time() - start_time
            result['status_code'] = response.status_code
            
            # Analisar resposta HTTP
            http_indicators = self._check_http_indicators(response)
            if http_indicators:
                result['waf_detected'] = True
                result['waf_indicators'].extend(http_indicators)
            
            # Determinar tipo de WAF
            if result['waf_indicators']:
                result['waf_type'] = self._determine_waf_type(result['waf_indicators'])
            
        except requests.exceptions.RequestException as e:
            result['error'] = str(e)
            logger.warning(f"Erro ao acessar {url}: {e}")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Erro inesperado ao verificar {url}: {e}")
        
        return result
    
    def _check_dns_indicators(self, domain: str) -> List[str]:
        """Verifica indicadores de WAF no DNS"""
        indicators = []
        
        try:
            # Verificar registros TXT
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                for record in txt_records:
                    txt_data = str(record)
                    for waf_name, patterns in self.waf_patterns.items():
                        if any(pattern in txt_data.lower() for pattern in patterns):
                            indicators.append(f"DNS_TXT_{waf_name}")
            except dns.resolver.NXDOMAIN:
                pass
            except dns.resolver.NoAnswer:
                pass
            
            # Verificar registros CNAME para CDNs conhecidos
            try:
                cname_records = dns.resolver.resolve(domain, 'CNAME')
                for record in cname_records:
                    cname_data = str(record.target).lower()
                    if any(cdn in cname_data for cdn in ['cloudflare', 'akamai', 'fastly', 'cloudfront']):
                        indicators.append(f"DNS_CNAME_{cdn}")
            except dns.resolver.NoAnswer:
                pass
                
        except Exception as e:
            logger.debug(f"Erro ao verificar DNS para {domain}: {e}")
        
        return indicators
    
    def _check_http_indicators(self, response: requests.Response) -> List[str]:
        """Verifica indicadores de WAF na resposta HTTP"""
        indicators = []
        
        # Verificar headers
        for header_name, header_value in response.headers.items():
            header_lower = header_name.lower()
            header_value_lower = str(header_value).lower()
            
            for waf_name, patterns in self.waf_patterns.items():
                if any(pattern in header_lower or pattern in header_value_lower for pattern in patterns):
                    indicators.append(f"HTTP_HEADER_{waf_name}")
        
        # Verificar cookies
        for cookie in response.cookies:
            cookie_name = cookie.name.lower()
            for waf_name, patterns in self.waf_patterns.items():
                if any(pattern in cookie_name for pattern in patterns):
                    indicators.append(f"HTTP_COOKIE_{waf_name}")
        
        # Verificar corpo da resposta
        try:
            content = response.text.lower()
            for waf_name, patterns in self.waf_patterns.items():
                if any(pattern in content for pattern in patterns):
                    indicators.append(f"HTTP_BODY_{waf_name}")
        except:
            pass
        
        return indicators
    
    def _determine_waf_type(self, indicators: List[str]) -> str:
        """Determina o tipo de WAF baseado nos indicadores"""
        waf_counts = {}
        
        for indicator in indicators:
            waf_name = indicator.split('_')[-1]
            waf_counts[waf_name] = waf_counts.get(waf_name, 0) + 1
        
        if waf_counts:
            return max(waf_counts, key=waf_counts.get)
        
        return "unknown"
    
    def save_results(self, results: List[Dict], output_format: str = "both"):
        """Salva resultados em CSV e/ou JSON"""
        timestamp = int(time.time())
        
        if output_format in ["csv", "both"]:
            csv_filename = f"waf_check_results_{timestamp}.csv"
            self._save_csv(results, csv_filename)
        
        if output_format in ["json", "both"]:
            json_filename = f"waf_check_results_{timestamp}.json"
            self._save_json(results, json_filename)
    
    def _save_csv(self, results: List[Dict], filename: str):
        """Salva resultados em CSV"""
        if not results:
            return
        
        # Preparar dados para CSV
        csv_data = []
        for result in results:
            csv_data.append({
                'URL': result['url'],
                'WAF_Detectado': 'Sim' if result['waf_detected'] else 'Não',
                'Tipo_WAF': result['waf_type'] or 'N/A',
                'Indicadores': '; '.join(result['waf_indicators']) if result['waf_indicators'] else 'N/A',
                'Status_HTTP': result['status_code'] or 'N/A',
                'Tempo_Resposta': f"{result['response_time']:.3f}s" if result['response_time'] else 'N/A',
                'Erro': result['error'] or 'N/A'
            })
        
        df = pd.DataFrame(csv_data)
        
        if self.local_mode:
            filepath = os.path.join('output', filename)
            os.makedirs('output', exist_ok=True)
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"CSV salvo localmente: {filepath}")
        else:
            self._upload_to_s3(df.to_csv(index=False, encoding='utf-8'), filename, 'text/csv')
    
    def _save_json(self, results: List[Dict], filename: str):
        """Salva resultados em JSON"""
        if not results:
            return
        
        json_data = {
            'metadata': {
                'timestamp': int(time.time()),
                'total_urls': len(results),
                'waf_detected_count': sum(1 for r in results if r['waf_detected']),
                'waf_not_detected_count': sum(1 for r in results if not r['waf_detected'])
            },
            'results': results
        }
        
        if self.local_mode:
            filepath = os.path.join('output', filename)
            os.makedirs('output', exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.info(f"JSON salvo localmente: {filepath}")
        else:
            self._upload_to_s3(json.dumps(json_data, indent=2, ensure_ascii=False), filename, 'application/json')
    
    def _upload_to_s3(self, content: str, filename: str, content_type: str):
        """Faz upload de arquivo para S3"""
        if not self.s3_bucket:
            logger.warning("Bucket S3 não configurado, salvando localmente")
            filepath = os.path.join('output', filename)
            os.makedirs('output', exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return
        
        try:
            s3 = self.session.client('s3')
            s3.put_object(
                Bucket=self.s3_bucket,
                Key=filename,
                Body=content,
                ContentType=content_type
            )
            logger.info(f"Arquivo enviado para S3: s3://{self.s3_bucket}/{filename}")
        except Exception as e:
            logger.error(f"Erro ao enviar para S3: {e}")
            # Fallback para salvamento local
            filepath = os.path.join('output', filename)
            os.makedirs('output', exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Arquivo salvo localmente como fallback: {filepath}")

@click.command()
@click.option('--local', 'local_mode', is_flag=True, help='Executar em modo local (sem Docker)')
@click.option('--local-storage', 'local_storage', is_flag=True, help='Salvar arquivos localmente ao invés de S3')
@click.option('--urls-file', 'urls_file', type=click.Path(exists=True), help='Arquivo com URLs para testar (uma por linha)')
@click.option('--max-urls', 'max_urls', type=int, help='Número máximo de URLs para testar')
@click.option('--hosted-zone-id', 'hosted_zone_id', help='ID da zona hospedada Route53 específica')
@click.option('--output-format', 'output_format', type=click.Choice(['csv', 'json', 'both']), default='both', help='Formato de saída')
@click.option('--help', 'show_help', is_flag=True, help='Mostrar esta mensagem de ajuda')
def main(local_mode, local_storage, urls_file, max_urls, hosted_zone_id, output_format, show_help):
    """
    Sistema de Verificação de WAF
    
    Este sistema verifica se URLs estão protegidas por WAF através de:
    - Análise de registros DNS do Route53
    - Verificação de indicadores HTTP
    - Análise de cookies e headers
    
    PARÂMETROS:
    --local: Executa o sistema em modo local (sem Docker)
    --local-storage: Salva arquivos localmente ao invés de fazer upload para S3
    --urls-file: Arquivo local com URLs para testar (uma por linha)
    --max-urls: Limita o número de URLs testadas
    --hosted-zone-id: ID específico da zona hospedada Route53
    --output-format: Formato de saída (csv, json, ou both)
    
    EXEMPLOS:
    python waf_checker.py --local --local-storage
    python waf_checker.py --urls-file urls.txt --max-urls 100
    python waf_checker.py --hosted-zone-id Z1234567890ABC
    """
    
    if show_help:
        click.echo(main.get_help())
        return
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurar modo de execução
    if local_mode:
        os.environ['LOCAL_MODE'] = 'true'
    
    # Configurar armazenamento
    s3_bucket = None if local_storage else os.getenv('S3_BUCKET')
    
    # Criar instância do verificador
    checker = WAFChecker(local_mode=local_mode, s3_bucket=s3_bucket)
    
    try:
        # Obter URLs para testar
        if urls_file:
            logger.info(f"Carregando URLs do arquivo: {urls_file}")
            urls = checker.load_urls_from_file(urls_file, max_urls)
        else:
            logger.info("Listando registros DNS do Route53...")
            urls = checker.get_route53_records(hosted_zone_id, max_urls)
        
        if not urls:
            logger.warning("Nenhuma URL encontrada para testar")
            return
        
        logger.info(f"Iniciando verificação de WAF para {len(urls)} URLs...")
        
        # Verificar WAF para cada URL
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Verificando {i}/{len(urls)}: {url}")
            result = checker.check_waf_protection(url)
            results.append(result)
            
            # Pequena pausa para não sobrecarregar servidores
            time.sleep(0.5)
        
        # Salvar resultados
        logger.info("Salvando resultados...")
        checker.save_results(results, output_format)
        
        # Resumo
        waf_detected = sum(1 for r in results if r['waf_detected'])
        logger.info(f"Verificação concluída!")
        logger.info(f"Total de URLs: {len(urls)}")
        logger.info(f"WAF detectado: {waf_detected}")
        logger.info(f"Sem WAF: {len(urls) - waf_detected}")
        
    except KeyboardInterrupt:
        logger.info("Operação interrompida pelo usuário")
    except Exception as e:
        logger.error(f"Erro durante execução: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
