# backup

Sistema de backup automatizado PostgresSQL com gerenciamento Google Drive


## Documentação 

https://developers.google.com/drive/api/quickstart/python?hl=pt-br


## Instalação

Após clonar o projeto e instalar as dependências, mova os arquivos `token.json` e `credentials.json` para o remoto.

Confirme se os scripts possuem permissão de execução 755. 

Copie as linhas do `scripts/cron.txt` para dentro do `crontab -e` ou `sudo crontab -e` para executar como root