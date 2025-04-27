# 🛒 Dynamic Pricing API with Reinforcement Learning

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-green?logo=django)](https://www.djangoproject.com/)
[![Stable Baselines3](https://img.shields.io/badge/Stable--Baselines3-RL-blueviolet)](https://stable-baselines3.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

This project is a Django-based API for e-commerce dynamic pricing, powered by **Reinforcement Learning** (OpenAI Gym + Stable Baselines3).  
Each product learns how to adjust its price based on stock levels, sales, and historical data — **automatically**.

---

## 🚀 Features

- Django backend with **GraphQL API** for product management
- **Custom OpenAI Gym environment** for dynamic pricing simulation
- **DQN Agent** for price optimization
- Train, save, and load models per product
- Easy CLI management command to update prices
- Pipenv environment management

---

## 🛠️ Built With

- Python 3.11
- Django 4.x
- Graphene-Django (GraphQL)
- OpenAI Gym
- Stable-Baselines3 (DQN)
- Pipenv

---

## ⚙️ Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/YOUR_USERNAME/dynamic_pricing_api.git
    cd dynamic_pricing_api
    ```

2. Install dependencies:

    ```bash
    pipenv install
    ```

3. Apply database migrations:

    ```bash
    python manage.py migrate
    ```

4. (Optional) Create a superuser:

    ```bash
    python manage.py createsuperuser
    ```

5. Run the server:

    ```bash
    python manage.py runserver
    ```

---

## 📈 Usage

- Update product prices:

    ```bash
    python manage.py update_prices
    ```

- (Optional) Train new models with custom timesteps:

    ```bash
    python manage.py update_prices --train-new --timesteps 10000
    ```

---

## 🧩 GraphQL Example

Fetch all products:

```graphql
{
  allProducts {
    id
    name
    currentPrice
    minPrice
    maxPrice
    stock
  }
}


GraphQL endpoint: http://localhost:8000/graphql/

## 📂 Project Structure

dynamic_pricing_api/
├── products/           # Product models and GraphQL schema
├── rl_pricing/          # Reinforcement Learning trainer & environment
├── manage.py
├── Pipfile / Pipfile.lock
├── README.md
└── requirements.txt


## 🛣️ Roadmap
 Add PPO, A2C agents

 Async training

 Advanced reward shaping

 Docker containerization

 Admin UI for model insights



## 📜 License
Distributed under the MIT License. See LICENSE for more information.



🙌 Acknowledgements
Django

Stable-Baselines3

OpenAI Gym

Graphene-Django



Made with ❤️ by Rayane Kahlaoui