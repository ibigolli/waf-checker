#!/usr/bin/env python3
"""
Script de teste para execução local do sistema de verificação de WAF
"""

import os
import sys
from waf_checker import WAFChecker

def test_local_execution():
    """Testa execução local do sistema"""
    print("🧪 Testando execução local do sistema de verificação de WAF...")
    
    # Configurar para modo local
    os.environ['LOCAL_MODE'] = 'true'
    
    # Criar instância do verificador
    checker = WAFChecker(local_mode=True, s3_bucket=None)
    
    # URLs de teste
    test_urls = [
        'https://example.com',
        'https://httpbin.org',
        'https://httpstat.us/200'
    ]
    
    print(f"📋 Testando {len(test_urls)} URLs...")
    
    results = []
    for i, url in enumerate(test_urls, 1):
        print(f"🔍 Verificando {i}/{len(test_urls)}: {url}")
        result = checker.check_waf_protection(url)
        results.append(result)
        
        # Mostrar resultado
        status = "✅ WAF Detectado" if result['waf_detected'] else "❌ Sem WAF"
        print(f"   {status} - Tipo: {result['waf_type'] or 'N/A'}")
    
    # Salvar resultados
    print("\n💾 Salvando resultados...")
    checker.save_results(results, "both")
    
    # Resumo
    waf_detected = sum(1 for r in results if r['waf_detected'])
    print(f"\n📊 Resumo:")
    print(f"   Total de URLs: {len(test_urls)}")
    print(f"   WAF detectado: {waf_detected}")
    print(f"   Sem WAF: {len(test_urls) - waf_detected}")
    
    print("\n✅ Teste local concluído com sucesso!")
    print("📁 Verifique a pasta 'output' para os arquivos gerados.")

if __name__ == '__main__':
    try:
        test_local_execution()
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        sys.exit(1)
