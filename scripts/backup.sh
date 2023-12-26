#!/bin/bash

set -e

# Verifica se o script é executado como superusuário (root)
if [ "$(id -u)" != "0" ]; then
  echo "Este script deve ser executado como superusuário (root)."
  exit 1
fi

# Variaveis de Ambiente

SEU_USUARIO=user

EMAIL=email@email.com

DATA=$(date +%Y-%m-%d_%H-%M)

# Diretorio local de backup
PBACKUP="/home/$SEU_USUARIO/backup"


# LIMPEZA
# Os arquivos dos ultimos NDIAS dias serao mantidos
NDIAS="30"

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

	find ${PBACKUP} -type d -mtime +$NDIAS -exec rm -rf {} \;
fi


### Postgres

if [ ! -d $PBACKUP/$DATA/postgres ]; then
    mkdir -p $PBACKUP/$DATA/postgres
fi

chown -R postgres:postgres $PBACKUP/$DATA/postgres/

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
su -c 'echo "Backup finalizado" |mutt -s "Backup $HOST Finalizado!" $EMAIL' -s '/bin/bash' $SEU_USUARIO

exit 0