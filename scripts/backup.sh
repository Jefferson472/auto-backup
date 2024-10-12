#!/bin/bash

set -e

# Verifica se o script é executado como superusuário (root)
if [ "$(id -u)" != "0" ]; then
  echo "Este script deve ser executado como superusuário (root)."
  exit 1
fi

# Carregar variáveis do arquivo .env
if [ -f .env ]; then
    source .env
else
    echo "Arquivo .env não encontrado. O script será interrompido."
    exit 1  # Saída com código de erro 1
fi

# Variaveis de Ambiente

DATA=$(date +%Y-%m-%d)

# Diretorio local de backup
PBACKUP=$PATH_TO_BACKUP_FOLDER


# LIMPEZA
# Os arquivos dos ultimos NDIAS dias serao mantidos
NDIAS=$POLITICA_ARMAZANAMENTO_LOCAL

if [ ! -d ${PBACKUP} ]; then
	echo ""
	echo " A pasta de backup nao foi encontrada!"
	mkdir -p ${PBACKUP}
	echo " Iniciando Tarefa de backup..."
	echo ""
else
	echo ""
	echo " Rotacionando backups mais antigos que $NDIAS"
	echo ""

	find ${PBACKUP} -type d -mtime +$((NDIAS)) -exec rm -rf {} \; || true
fi


### Postgres

# Verifica se o usuário postgres existe
if ! id -u postgres > /dev/null 2>&1; then
    echo "Usuário postgres não existe. Criando..."
    # Cria o usuário postgres
    sudo adduser --system --group --no-create-home postgres
fi

if [ ! -d $PBACKUP/$DATA/postgres ]; then
    mkdir -p $PBACKUP/$DATA/postgres
    chown -R postgres:postgres $PBACKUP/$DATA/postgres/
    chmod -R g+w $PBACKUP/$DATA
fi

su - postgres -c "vacuumdb -a -f -z"

for basepostgres in $(su - postgres -c "psql -l" | grep -v template0|grep -v template1|grep "|" |grep -v Owner |awk '{if ($1 != "|" && $1 != "Nome") print $1}'); do

    su - postgres -c "pg_dump --format=c $basepostgres > $PBACKUP/$DATA/postgres/$basepostgres.dump"

    cd $PBACKUP/$DATA/postgres/

    tar -czvf $basepostgres.dump.tar.gz $basepostgres.dump

    rm -rf $basepostgres.dump

	cd /

done

# Backup de usuarios do Postgresql

su - postgres -c "pg_dumpall --globals-only -S postgres > $PBACKUP/$DATA/postgres/usuarios.sql"

# envia um email ao final da execução
echo "Enviando email"
su - $USUARIO -c "echo 'Backup finalizado' | mutt -s 'Backup $HOSTNAME Finalizado!' $RECEIVER_EMAIL"

exit 0
