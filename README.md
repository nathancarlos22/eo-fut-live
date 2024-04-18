## Sumário

- [Introdução](#introdu%C3%A7%C3%A3o)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Como Usar](#como-usar)

## Introdução

Este projeto tem como objetivo analisar jogos de futebol ao vivo e prever a ocorrência do primeiro gol na partida. Para isso, foi coletado dados de jogos diários ao vivo por um período de mais de um ano e treinado modelos de aprendizagem de máquina.

## Funcionalidades

1.  **Coleta de Dados**: Web scraping em tempo real do site [Opta Player Stats](https://optaplayerstats.statsperform.com).
2.  **Modelagem**: Utilização de uma rede neural com Keras e um modelo AutoML TPOT.
3.  **Notificação**: Envio de notificações via bot do Telegram quando a previsão atinge um score específico.

## Tecnologias Utilizadas

- Python 3.1.x
- Keras
- H2O AutoML
- Selenium (para web scraping)
- API Sportsanalytics.com.br

## Dataset

Os datasets utilizados para treinar os modelos,  o dataset coletado através de web scraping contém mais de 1 milhão de registros, ele se chama "data_live_scores_full" e os outros datasets são as janelas de tempo que foram utilizadas para o treinamento dos modelos. Você pode acessar e baixar o dataset através deste [link do Google Drive](https://drive.google.com/drive/folders/1YZS-NPt8ZFMS3iD4dnNTIY9TZeooUEa7?usp=drive_link).

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

