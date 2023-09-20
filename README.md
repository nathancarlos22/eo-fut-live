## Sumário

- [Introdução](#introdu%C3%A7%C3%A3o)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Como Usar](#como-usar)
- [Contribuição](#contribui%C3%A7%C3%A3o)
- [Licença](#licen%C3%A7a)

## Introdução

Este projeto tem como objetivo analisar jogos de futebol ao vivo e prever se um gol será marcado no primeiro tempo do jogo. Para isso, foi coletado dados de jogos diários ao vivo por um período de mais de um ano e treinado modelos de aprendizagem de máquina.

## Funcionalidades

1.  **Coleta de Dados**: Web scraping em tempo real do site [Opta Player Stats](https://optaplayerstats.statsperform.com).
2.  **Preprocessamento de Dados**: Balanceamento e limpeza dos dados coletados.
3.  **Modelagem**: Utilização de uma rede neural com Keras e um modelo AutoML com H2O.
4.  **Notificação**: Envio de notificações via bot do Telegram quando a previsão atinge um score específico.

## Tecnologias Utilizadas

- Python 3.1.x
- Keras
- H2O AutoML
- Selenium (para web scraping)
- API Sportsanalytics.com.br
- Telegram Bot API

## Dataset

O dataset utilizado para treinar os modelos foi coletado através de web scraping e contém mais de 1 milhão de registros. Você pode acessar e baixar o dataset através deste [link do Google Drive](https://drive.google.com/file/d/1LhHfpph0h02yt5DaYRleUEjvSlCqVJBH/view?usp=drive_link).

## Como Usar

1.  Instale as dependências:

    `pip install -r requirements.txt`

2.  Para coletar os dados, execute:

    ```bash
    python notebooks/make-data-wbscrap.ipynb
    ```

    Ou use os scripts Python correspondentes em `/src`.

3.  Para treinar os modelos, execute:

    ```bash
    python notebooks/nc-model-pred-live.ipynb
    ```

4.  Para rodar as previsões ao vivo, execute:

    ```css
    python main.py
    ```

## Projetos Futuros

- Integração com a API da Betfair para automatizar apostas com base nas previsões do modelo.
