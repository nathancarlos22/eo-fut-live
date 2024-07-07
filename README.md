## Sumário

- [Introdução](#introdu%C3%A7%C3%A3o)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Como Usar](#como-usar)

## Introdução

Esta é uma ferramenta que tem como objetivo analisar jogos de futebol ao vivo e prever a ocorrência do primeiro gol na partida. Para isso, foi coletado dados de jogos diários ao vivo por um período de mais de um ano e treinado modelos de aprendizagem de máquina.

## Funcionalidades

1.  **Coleta de Dados**: Web scraping em tempo real do site [Opta Player Stats](https://optaplayerstats.statsperform.com).
2.  **Avaliação dos dados**: Faz o pré-processamento e avalia os atributos dos dados.
3.  **Modelagem**: Utilização modelo AutoML TPOT.
4.  **Notificação**: Envio de notificações via bot do Telegram quando a previsão atinge um score específico.

## Tecnologias Utilizadas

- Python 3.1.x
- Keras
- Selenium (para web scraping)
- Automl TPOT

## Dataset

Os datasets utilizados para treinar os modelos,  o dataset coletado através de web scraping contém mais de 1 milhão de registros, ele se chama "data_live_scores_full" e os outros datasets são as janelas de tempo que foram utilizadas para o treinamento dos modelos. Você pode acessar e baixar o dataset através deste [link do Google Drive](https://drive.google.com/drive/folders/1YZS-NPt8ZFMS3iD4dnNTIY9TZeooUEa7?usp=drive_link).

## Como Usar

1.  Instale as dependências:

    `pip install -r requirements.txt`

Obs: Se quiser executar a ferramenta com os dados de jogos do dataset que já foi coletado e avaliado, pule para a etapa 4.

2. Para fazer a coleta de dados de jogos atuais, execute o arquivo `make-data.py`, altere a data da variável `date_strings` para fazer a coleta dessa data até a data do dia de hoje.
   Obs: Esta etapa precisa de um container docker, crie um container docker baixando a ferramenta `docker desktop`.

3.  Para treinar os modelos, é preciso avaliar todos os dados novamente, execute sequencialmente os arquivos jupyter `after_engineering.ipynb`, `balanceando e tratando.ipynb` , `model-automl.ipynb` 

4.  Crie um arquivo `.env` e adicione as credenciais do telegrama para que a ferramenta envie mensagens para o seu grupo ao encontrar um jogo ao vivo com previsão de um gol.
    Arquivo `.env` exemplo:
    
    ```
    CHAT_ID='-100165'`
    TOKEN='6254535706:AAjzVyaJ5f8A_'
    
    ```
    
 5. Para executar as previsões ao vivo, execute:

    ```css
    python main.py
    ```
