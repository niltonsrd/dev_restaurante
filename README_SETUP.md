# 🍽️ Sistema de Cardápio com Área Administrativa

Este projeto é um sistema completo de cardápio online integrado com uma área administrativa protegida por senha. Ele permite que usuários acessem o cardápio, façam pedidos via WhatsApp e que administradores gerenciem produtos diretamente pelo navegador.

---

## 🚀 Funcionalidades do Sistema

### **🟢 Área Pública (Clientes)**

* Visualização de cardápio
* Itens agrupados por categorias
* Botão de adicionar/remover itens do pedido
* Revisão do pedido em tempo real
* Envio automático do pedido via WhatsApp
* Exibição de forma de pagamento via PIX (com QR Code)
* Layout responsivo

---

### **🔒 Área Administrativa (Protegida)**

* Login seguro com senha
* Listagem de produtos cadastrados
* Adicionar novos produtos
* Editar produtos existentes
* Excluir produtos
* Logout que redireciona para o cardápio
* Proteção de rotas (não acessa /admin sem login)

---

## 🛠️ Tecnologias Utilizadas

* **Flask (Python)** — backend e rotas
* **SQLite** — banco de dados local
* **HTML + CSS** — interface
* **JavaScript** — lógicas de pedido e integração com WhatsApp
* **qrcodeapi** — geração de QR Code PIX

---

## 📁 Estrutura do Projeto

```
📂 projeto/
├── app.py
├── database.db
├── /static
│   ├── /css
│   │   └── styles.css
│   ├── /js
│   │   └── script.js
│   └── /img
├── /templates
│   ├── index.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── editar_produto.html
└── README.md
```

---

## 🔧 Configuração e Instalação

### **1. Clonar o repositório**

```bash
git clone https://github.com/seu_usuario/seu_repositorio.git
cd seu_repositorio
```

### **2. Criar ambiente virtual (opcional, recomendado)**

```bash
python -m venv venv
```

### **3. Ativar ambiente virtual**

* **Windows**:

```bash
venv\Scripts\activate
```

* **Linux/Mac**:

```bash
source venv/bin/activate
```

### **4. Instalar dependências**

```bash
pip install flask
```

### **5. Executar o sistema**

```bash
python app.py
```

Acesse no navegador:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔐 Acesso à Área Administrativa

A página administrativa está localizada em:

```
/admin
```

A senha padrão é definida diretamente no arquivo `app.py`.

Você pode alterar assim:

```python
ADMIN_PASSWORD = "minha_nova_senha"
```

---

## 🧾 Banco de Dados

O banco utilizado é **SQLite**, criado automaticamente caso não exista.

Tabela principal: `produtos`

Campos:

* id (INT)
* nome (TEXT)
* preco (REAL)
* categoria (TEXT)
* imagem (TEXT)

---

## 📌 Segurança

* Rotas administrativas protegidas por sessão
* Logout funcional
* Dados sensíveis não ficam expostos no código JS
* Código organizado para evitar acesso indevido

---

## 🖼️ Layout e Experiência

* Totalmente responsivo
* Interface moderna e intuitiva
* Painel administrativo limpo e objetivo
* Sistema de pedidos direto pelo WhatsApp

---

## ❤️ Autor

Projeto desenvolvido para estudos em desenvolvimento web.

Se quiser melhorar o projeto, fique à vontade para enviar um Pull Request!

---

## 📞 Suporte

Se precisar de ajuda, abra uma **Issue** no repositório ou me chame.
