# Record Management System (Sistema de Gestão de Registros)

## Descrição
Um sistema web robusto para gerenciar eficientemente registros de sentenciados, controlar visitas e organizar listas de visitantes com persistência em MongoDB. Esta aplicação oferece uma interface intuitiva para pesquisar registros por diversos critérios e criar listas personalizadas para controle de entrada e saída de visitantes.

## Índice
1. [Funcionalidades](#funcionalidades)
2. [Arquitetura](#arquitetura)
3. [Pré-requisitos](#pré-requisitos)
4. [Instalação](#instalação)
5. [Execução](#execução)
6. [Uso](#uso)
7. [Estrutura do Projeto](#estrutura-do-projeto)
8. [Contribuição](#contribuição)
9. [Licença](#licença)

## Funcionalidades

### Pesquisa Avançada
- Busca por número de matrícula
- Busca por nome com correspondência insensível a maiúsculas/minúsculas
- Suporte a busca parcial de nomes

### Gestão de Visitantes
- Registro de entrada de visitantes por sentenciado
- Controle de quantidade de visitantes (homens, mulheres, crianças)
- Registro de garrafas PET trazidas pelos visitantes

### Listas Personalizadas
- Criação de listas de visitantes
- Ordenação por diferentes critérios (nome, matrícula, etc.)
- Remoção de registros da lista
- Exportação da lista em formato PDF

### Dashboard Informativo
- Visualização de totais por pavilhão
- Resumo de visitantes (homens, mulheres, crianças)
- Contagem de garrafas PET

### Interface Amigável
- Design responsivo para desktop e dispositivos móveis
- Navegação intuitiva
- Exibição clara dos resultados

## Arquitetura
Este aplicativo segue a arquitetura MVC (Model-View-Controller):
- Frontend: HTML/CSS com Bootstrap e JavaScript
- Backend: Python Flask
- Banco de Dados: MongoDB
- Relatórios: ReportLab
- Comunicação: API RESTful

## Pré-requisitos
- Python 3.x
- MongoDB
- pip
- Git

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/fernandopereira3/novela.git
```

2. Navegue até o diretório:
```bash
cd novela
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Inicie o MongoDB:
```bash
# Linux/Mac
mongod

# Windows: Verifique se o serviço está ativo
```

## Execução

### Desenvolvimento
```bash
python main.py
```
Acesse: http://localhost:5000 ou http://ip-do-servidor:5000

### Produção (Linux/Mac)
```bash
# Usando nohup
nohup python main.py > output.log 2>&1 &

# Usando screen
screen -S novela
python main.py

# Usando tmux
tmux new -s novela
python main.py
```

### Produção (Windows)
```powershell
# PowerShell
Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Hidden

# NSSM (Como Serviço)
nssm.exe install NovelaPython
nssm.exe start NovelaPython
```

## Uso

### Pesquisando Registros
1. Acesse a página principal
2. Digite matrícula ou nome
3. Clique em "PESQUISAR"
4. Visualize resultados

### Registrando Visitantes
1. Pesquise o sentenciado
2. Preencha quantidades
3. Adicione à lista
4. Verifique a lista atualizada

### Gerenciando Lista
1. Acesse "Lista de Selecionados"
2. Ordene conforme necessário
3. Gerencie registros
4. Exporte ou salve a lista

## Estrutura do Projeto
```
novela/
├── main.py
├── rotas.py
├── rotas_saida.py
├── debug.py
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── templates/
│   ├── index.html
│   ├── pesquisa.html
│   ├── lista.html
│   └── debug.html
└── requirements.txt
```

## Contribuição
1. Faça um fork
2. Crie um branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.