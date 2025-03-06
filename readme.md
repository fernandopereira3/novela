# Record Management System (Sistema de Gestão de Registros)

![License](https://img.shields.io/badge/license-MIT-blue.svg)

A robust web-based solution for efficiently managing, searching, and organizing records with MongoDB persistence. This application offers an intuitive interface for searching records by various criteria and creating customized lists.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Versão em Português](#versão-em-português)

## ✨ Features

- **Powerful Search Capabilities**:
  - Search by registration number (matrícula)
  - Search by name with case-insensitive matching
  - Partial name search support
  
- **Custom Record Lists**:
  - Select specific records and add them to a custom list
  - Manage multiple selected records at once
  - View, edit, and export custom lists
  
- **User-Friendly Interface**:
  - Responsive design that works on desktop and mobile devices
  - Intuitive navigation and operation
  - Clear display of search results
  
- **Data Persistence**:
  - MongoDB integration for reliable data storage
  - Efficient data retrieval and management

- **PIP error**:
  - This error is because the pip command is not recognized.
  - To fix this error, you need to install the pip package.
  - You can install the pip package with the command:
  ```bash
  sudo apt-get install python3-pip
  ```

## 🏗️ Architecture

This application follows a simple MVC (Model-View-Controller) architecture:

- **Frontend**: HTML/CSS with JavaScript for dynamic interactions
- **Backend**: Python Flask framework handling requests and business logic
- **Database**: MongoDB for data persistence
- **Communication**: RESTful API endpoints connecting frontend and backend

## 🔧 Prerequisites

Before installation, ensure you have:

- Python 3.x
- MongoDB
- pip (Python package manager)
- Git (for cloning the repository)

## 📥 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/fernandopereira3/lista.git
   ```

2. Navigate to the project directory:
   ```bash
   cd lista
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure MongoDB is running on your system:
   ```bash
   mongod
   ```

5. Start the application:
   ```bash
   python app.py
   ```

6. Access the application at `http://localhost:5000` in your web browser

## 🚀 Usage

### Searching Records

1. Enter a registration number or name in the search field
2. Click the search button or press Enter
3. View matching results displayed below

### Creating Custom Lists

1. Search for records using the search function
2. Select desired records by clicking the checkbox next to each entry
3. Click "Add to List" to include selected records in your custom list
4. View your custom list by navigating to the "Selected Records" page

### Managing Lists

1. Navigate to "Selected Records" to view your custom list
2. Remove unwanted entries as needed
3. Export list data for external use

## 📚 API Documentation

The application provides the following API endpoints:

- `GET /api/records?query={search_term}` - Search records by name or registration number
- `POST /api/list` - Add records to custom list
- `GET /api/list` - Retrieve all records in current custom list
- `DELETE /api/list/{record_id}` - Remove a record from custom list

## 📁 Project Structure

```
lista/
│
├── app.py              # Main application entry point
├── static/             # Static files (CSS, JavaScript)
│   ├── css/            # Stylesheets
│   └── js/             # Client-side scripts
├── templates/          # HTML templates
├── models/             # Database models
├── controllers/        # Application logic
├── tests/              # Test suite
└── requirements.txt    # Python dependencies
```

## 👥 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

# Versão em Português

## Sistema de Gestão de Registros

Uma solução web robusta para gerenciar, pesquisar e organizar registros eficientemente com persistência em MongoDB. Esta aplicação oferece uma interface intuitiva para buscar registros por diversos critérios e criar listas personalizadas.

## Funcionalidades

- **Poderosos Recursos de Busca**:
  - Busca por número de matrícula
  - Busca por nome (não sensível a maiúsculas/minúsculas)
  - Suporte a busca parcial de nomes
  
- **Listas Personalizadas de Registros**:
  - Selecione registros específicos e adicione-os a uma lista personalizada
  - Gerencie múltiplos registros selecionados de uma vez
  - Visualize, edite e exporte listas personalizadas
  
- **Interface Amigável**:
  - Design responsivo que funciona em dispositivos desktop e móveis
  - Navegação e operação intuitivas
  - Exibição clara dos resultados de busca
  
- **Persistência de Dados**:
  - Integração com MongoDB para armazenamento confiável de dados
  - Recuperação e gerenciamento eficiente de dados

## Arquitetura

Esta aplicação segue uma arquitetura MVC (Model-View-Controller) simples:

- **Frontend**: HTML/CSS com JavaScript para interações dinâmicas
- **Backend**: Framework Python Flask para manipulação de requisições e lógica de negócios
- **Banco de Dados**: MongoDB para persistência de dados
- **Comunicação**: Endpoints de API RESTful conectando frontend e backend

## Pré-requisitos

Antes da instalação, certifique-se de ter:

- Python 3.x
- MongoDB
- pip (gerenciador de pacotes Python)
- Git (para clonar o repositório)

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/fernandopereira3/lista.git
   ```

2. Navegue até o diretório do projeto:
   ```bash
   cd lista
   ```

3. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

4. Certifique-se de que o MongoDB esteja em execução no seu sistema:
   ```bash
   mongod
   ```

5. Inicie a aplicação:
   ```bash
   python app.py
   ```

6. Acesse a aplicação em `http://localhost:5000` no seu navegador

## Uso

### Pesquisando Registros

1. Digite um número de matrícula ou nome no campo de busca
2. Clique no botão de busca ou pressione Enter
3. Visualize os resultados correspondentes exibidos abaixo

### Criando Listas Personalizadas

1. Pesquise registros usando a função de busca
2. Selecione os registros desejados clicando na caixa de seleção ao lado de cada entrada
3. Clique em "Adicionar à Lista" para incluir os registros selecionados em sua lista personalizada
4. Visualize sua lista personalizada navegando até a página "Registros Selecionados"

### Gerenciando Listas

1. Navegue até "Registros Selecionados" para visualizar sua lista personalizada
2. Remova entradas indesejadas conforme necessário
3. Exporte dados da lista para uso externo
