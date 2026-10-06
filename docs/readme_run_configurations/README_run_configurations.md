
# Run/Debug Configurations

## Configuració de test

![image](captura_pycharm_run_config_test.png)

Automàticament executa els tests del directori `src\tests`.
Consultar `README.md` en referència a `APP_MODE=test` per més informació.


## Configuracions de manteniment
Aquestes configuracions fan servir les comandes `db` de l'aplicació Flask.

### Maintenance: db help
La primera d'elles mostra l'ajuda de la comanda `db`:

![image](captura_pycharm_run_config_db_help.png)


### Maintenance: db init
Aquesta comanda inicialitza el repositori. Crea per primer cop el directori migrations.
Per reproduir la inicialització amb posterioritat cal:
* Esborrar la base de dades.
* Esborrar el directori migrations.

![image](captura_pycharm_run_config_db_init.png)

### Maintenance: db migrate
Aquesta comanda afegeix un nou arxiu de versió a migrations/version.
Recull els canvis fets a `db_models.py`
Per fer servir la comanda cal:
* Esborrar la base de dades.
* Executar la comanda upgrade, per crear la base de dades i deixar-la en l'estat de la darrera versió migrada.
* Executar la comanda migrate.
* Editar l'arxiu de versions i afegir-hi les comandes personalitzades a l'apartat `# ### Customized commands ###`

![image](captura_pycharm_run_config_db_migrate.png)

### Maintenance: db upgrade
Serveix per actualitzar la base de dades a la darrera versió migrada.

![image](captura_pycharm_run_config_db_upgrade.png)

Consultar `README.md` en referència a `APP_MODE=maintenance` per més informació.

## Configuració de desenvolupament/debug
Aquesta configuració executa el servei en mode normal.

![image](captura_pycharm_run_config_kapri2api.png)
Consultar `README.md` en referència a `APP_MODE` no definida o `APP_MODE=normal` per més informació.