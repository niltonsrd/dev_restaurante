Dev Restaurante — Sistema de Pedidos Online 🍔

Sistema web completo para restaurante, permitindo cadastro de produtos, seleção de itens no carrinho, cálculo automático de taxa de entrega por bairro, escolha de pagamento e envio do pedido para WhatsApp. Inclui painel administrativo protegido por senha para gerenciamento do cardápio.

📌 Tecnologias utilizadas

Backend: Python 3 + Flask

Banco de dados: SQLite

Frontend: HTML, CSS, JavaScript

Envio de pedidos: WhatsApp API

Uploads: Imagens de produtos e comprovantes PIX

Hospedagem de arquivos: static/img e static/pix_comprovantes

🛒 Funcionalidades
1️⃣ Cardápio e Carrinho

Produtos carregados dinamicamente do banco de dados.

Adição, remoção e alteração de quantidade de itens no carrinho.

Cálculo do subtotal em tempo real.

Interface responsiva e intuitiva.

Exemplo visual:


2️⃣ Taxa de entrega

Cada bairro tem uma taxa configurada no backend (/api/delivery-fees).

Seleção de bairro atualiza automaticamente:

Valor da taxa exibido na tela

Total do pedido (subtotal + taxa)

Valor exato enviado para o backend no checkout.

Exemplo visual:


3️⃣ Métodos de pagamento

Dinheiro: possibilidade de informar valor de troco.

Cartão: habilita botão de checkout diretamente.

PIX: upload de comprovante e geração de QR Code real.

Exemplo visual:


4️⃣ Checkout

Validação de campos obrigatórios: nome, endereço, bairro, carrinho e método de pagamento.

Geração automática de mensagem formatada para WhatsApp:

Detalhes do cliente

Itens do carrinho e subtotal

Taxa de entrega

Total final

Comprovante PIX (se enviado)

Redireciona para WhatsApp para envio do pedido.

Exemplo visual do pedido no WhatsApp:

🧾 Pedido - Dev Restaurante
👤 Cliente: Douglas
📍 Endereço: Campinas
🏙 Bairro: Pituaçu
📞 Contato: 71912345678
📝 Obs: Muito molho barbecue

💳 Pagamento: pix
💠 PIX enviado ✔

🍔 Itens:
- 1x Batata Frita — R$ 15.00
- 1x Refrigerante Lata — R$ 6.00
- 1x Cachorro-Quente — R$ 15.90

🚚 Entrega: R$ 7.00
💰 Total: R$ 43.90

📎 Comprovante PIX: <link>

5️⃣ Painel Administrativo

Protegido por senha (ADMIN_PASSWORD no .env ou default: admin123).

Funcionalidades:

Adicionar produtos (com imagem e descrição)

Editar produtos

Deletar produtos

Logout seguro com remoção de cookie.

Exemplo visual do admin:


📂 Estrutura de Pastas
dev_restaurante/
│
├─ app.py                 # Aplicação Flask
├─ database/
│   └─ database.db        # Banco de dados SQLite
├─ static/
│   ├─ img/               # Imagens de produtos
│   └─ pix_comprovantes/  # Comprovantes PIX enviados
├─ templates/
│   ├─ index.html         # Página principal (cardápio)
│   └─ admin.html         # Painel administrativo
└─ README.md

⚙️ Configurações importantes

Variáveis de ambiente:

ADMIN_PASSWORD → senha do painel administrativo

RESTAURANT_PHONE → número de WhatsApp para envio dos pedidos (formato internacional, ex: 5571991118924)

SERVER_URL → URL pública do site (opcional, usado para links de PIX)

FLASK_SECRET → chave secreta do Flask (para sessões e cookies)

Permissões de upload: Apenas arquivos com extensões .png, .jpg, .jpeg, .gif, .webp são permitidos.

🚀 Rodando o projeto localmente

Clonar o repositório:

git clone <repo-url>
cd dev_restaurante


Criar ambiente virtual e instalar dependências:

python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

pip install Flask


Executar a aplicação:

python app.py


Acessar no navegador:

http://127.0.0.1:5000/


Painel administrativo:

http://127.0.0.1:5000/admin

📌 Notas

A taxa de entrega é configurada no backend (/api/delivery-fees) e utilizada para cálculo do total.

Todos os uploads de PIX são salvos com nomes únicos para evitar sobrescrita.

Mensagem de pedido para WhatsApp é automaticamente formatada com Markdown para melhor visualização.

Qualquer bairro não listado usa a taxa padrão "Outro".