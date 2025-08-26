# Sistema de Verificação de WAF

Um sistema completo para verificar se URLs estão protegidas por Web Application Firewall (WAF) através de análise de DNS e requisições HTTP.

## 🚀 Funcionalidades

- **Listagem automática de entradas DNS** do Route53 da AWS
- **Gerenciamento de paginação** para grandes volumes de registros
- **Detecção inteligente de WAF** sem dependência do wafw00f
- **Saída em múltiplos formatos**: CSV e JSON
- **Execução via Docker** para produção
- **Modo local** para desenvolvimento e testes
- **Configuração flexível** de armazenamento (local ou S3)
- **Fonte de URLs configurável** (Route53 ou arquivo local)
- **Limitação configurável** do número de URLs testadas

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+** - Linguagem principal
- **Boto3** - Cliente AWS
- **Requests** - Requisições HTTP
- **DNS Python** - Resolução DNS
- **Click** - Interface de linha de comando
- **Pandas** - Manipulação de dados
- **Docker** - Containerização

## 📋 Pré-requisitos

### Para execução local:
- Python 3.11+
- Credenciais AWS configuradas
- Dependências Python instaladas

### Para execução Docker:
- Docker
- Docker Compose
- Credenciais AWS configuradas

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd waf-checker
```

### 2. Configure as variáveis de ambiente
```bash
cp env.example .env
# Edite o arquivo .env com suas credenciais AWS
```

### 3. Instale as dependências (execução local)
```bash
pip install -r requirements.txt
```

### 4. Configure credenciais AWS
```bash
# Via AWS CLI
aws configure

# Ou via variáveis de ambiente
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 🚀 Uso

### Execução Local

#### Verificar URLs do Route53:
```bash
python waf_checker.py --local --local-storage
```

#### Verificar URLs de arquivo local:
```bash
python waf_checker.py --local --local-storage --urls-file example_urls.txt
```

#### Limitar número de URLs:
```bash
python waf_checker.py --local --local-storage --max-urls 50
```

#### Especificar zona hospedada:
```bash
python waf_checker.py --local --local-storage --hosted-zone-id Z1234567890ABC
```

### Execução Docker

#### Construir imagem:
```bash
./run_docker.sh build
```

#### Executar sistema:
```bash
./run_docker.sh run --help
./run_docker.sh run --local-storage
./run_docker.sh run --urls-file example_urls.txt --max-urls 10
```

#### Executar teste local:
```bash
./run_docker.sh test
```

### Execução Direta com Docker Compose

```bash
# Construir e executar
docker-compose up --build

# Executar com parâmetros específicos
docker-compose run --rm waf-checker --local-storage --max-urls 100

# Executar teste
docker-compose run --rm waf-checker python test_local.py
```

## 📊 Parâmetros Disponíveis

| Parâmetro | Descrição | Padrão |
|-----------|-----------|---------|
| `--local` | Executa em modo local (sem Docker) | `false` |
| `--local-storage` | Salva arquivos localmente ao invés de S3 | `false` |
| `--urls-file` | Arquivo com URLs para testar (uma por linha) | `None` (usa Route53) |
| `--max-urls` | Número máximo de URLs para testar | `None` (testa todas) |
| `--hosted-zone-id` | ID específico da zona hospedada Route53 | `None` (todas as zonas) |
| `--output-format` | Formato de saída: csv, json, ou both | `both` |

## 🔍 Como Funciona a Detecção de WAF

O sistema utiliza múltiplas técnicas para detectar WAFs:

### 1. Análise DNS
- Verifica registros TXT para padrões de WAF
- Analisa registros CNAME para CDNs conhecidos
- Identifica serviços como Cloudflare, Akamai, Fastly

### 2. Análise HTTP
- Examina headers de resposta
- Verifica cookies específicos de WAF
- Analisa corpo da resposta para indicadores

### 3. Padrões Reconhecidos
- **Cloudflare**: `__cfduid`, `cf-ray`
- **AWS WAF**: `x-amz-cf-id`, `x-amz-cf-pop`
- **Akamai**: `x-akamai-transformed`
- **Imperva**: `incap_ses`, `visid_incap`
- **F5 BigIP**: `bigip`, `x-wa-info`
- E muitos outros...

## 📁 Estrutura de Arquivos

```
waf-checker/
├── waf_checker.py          # Sistema principal
├── test_local.py           # Script de teste local
├── requirements.txt        # Dependências Python
├── Dockerfile             # Configuração Docker
├── docker-compose.yml     # Orquestração Docker
├── run_docker.sh          # Script de execução Docker
├── env.example            # Exemplo de variáveis de ambiente
├── example_urls.txt       # URLs de exemplo para teste
├── output/                # Pasta de saída (criada automaticamente)
└── input/                 # Pasta de entrada (criada automaticamente)
```

## 📤 Formatos de Saída

### CSV
- URL
- WAF_Detectado (Sim/Não)
- Tipo_WAF
- Indicadores
- Status_HTTP
- Tempo_Resposta
- Erro

### JSON
```json
{
  "metadata": {
    "timestamp": 1234567890,
    "total_urls": 100,
    "waf_detected_count": 25,
    "waf_not_detected_count": 75
  },
  "results": [
    {
      "url": "https://example.com",
      "waf_detected": true,
      "waf_type": "cloudflare",
      "waf_indicators": ["HTTP_HEADER_cloudflare"],
      "status_code": 200,
      "response_time": 0.123,
      "error": null
    }
  ]
}
```

## 🔒 Configuração de Segurança

### Variáveis de Ambiente
- `AWS_ACCESS_KEY_ID`: Chave de acesso AWS
- `AWS_SECRET_ACCESS_KEY`: Chave secreta AWS
- `AWS_DEFAULT_REGION`: Região AWS padrão
- `S3_BUCKET`: Bucket S3 para armazenamento (opcional)

### Permissões AWS Necessárias
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "route53:ListHostedZones",
        "route53:ListResourceRecordSets"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

## 🧪 Testes

### Teste Local
```bash
python test_local.py
```

### Teste Docker
```bash
./run_docker.sh test
```

### Teste com URLs de Exemplo
```bash
python waf_checker.py --local --local-storage --urls-file example_urls.txt --max-urls 5
```

## 🐛 Solução de Problemas

### Erro de Credenciais AWS
```bash
aws configure
# Ou configure as variáveis de ambiente
```

### Erro de Permissões
Verifique se o usuário AWS tem permissões para:
- Route53: ListHostedZones, ListResourceRecordSets
- S3: PutObject (se usar S3)

### Erro de Conexão
- Verifique conectividade com internet
- Confirme configurações de proxy se aplicável
- Verifique firewall local

### Erro de Memória
- Use `--max-urls` para limitar URLs
- Execute em lotes menores

## 📈 Monitoramento e Logs

O sistema gera logs detalhados incluindo:
- Progresso da verificação
- URLs processadas
- WAFs detectados
- Erros encontrados
- Estatísticas finais

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação
- Verifique os logs de execução

## 🔄 Atualizações

### Versão Atual
- v1.0.0: Sistema base com detecção de WAF
- Suporte a Route53 e arquivos locais
- Saída em CSV e JSON
- Execução Docker e local

### Próximas Versões
- Interface web
- API REST
- Mais padrões de WAF
- Análise de performance
- Relatórios avançados