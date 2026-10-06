# Kapri2API

[![Test](https://github.com/arkimaldi/Kapri2API/actions/workflows/test.yml/badge.svg)](https://github.com/arkimaldi/Kapri2API/actions/workflows/test.yml)
[![Release](https://github.com/arkimaldi/Kapri2API/actions/workflows/release.yml/badge.svg)](https://github.com/arkimaldi/Kapri2API/actions/workflows/release.yml)

## Uso

### Compilación

Para compilar con Pyinstaller se llama al script `scripts/build`. Una vez completado, el binario estará listo en el directorio `dist`.

En `build` se registran los informes de la compilación. Si el binario no funcionara una vez instalado por la falta de algún modulo, estos ficheros pueden ayudar a diagnosticar el problema:

- `build/*/xref-*.html` - árbol de dependencias
- `build/*/warn-*.txt` - alertas emitidas por Pyinstaller

Para cross-compiling definir la variable de entorno `TARGET_ARCH`:

Pel mòdul Karo, compilem per l'arquitectura **arm64** fent:
* `TARGET_ARCH=arm64 ./scripts/build`


Si necessitem generar l'executable per a l'arquitectura  **aarch64**, que correspon a la versió arm de 64 bits, és a dir:
**arm64/v8** podem fer-ho així (Raspberry PI OS de 64 bits):
* `TARGET_ARCH=arm64/v8 ./scripts/build` 

Si necessitem generar l'executable per a l'arquitectura **arm/v7** podem fer-ho així (Nanopi):
* `TARGET_ARCH=arm/v7 ./scripts/build` 


### Paquete deb

Para producir un paquete para Debian usar `scripts/package`. Los paquetes resultantes se guardan en `packages`.

La version del paquete se define a partir del commit o tag del repositorio Git.

Igual que para compilar, para cross-compiling definir la variable de entorno `TARGET_ARCH`.

Pel mòdul Karo, empaquetem per l'arquitectura **arm64** fent:
* `TARGET_ARCH=arm64 ./scripts/package`


### Tests

Los tests se ejecutan en el entorno Docker. Para lanzarlos:

```sh
$ scripts/test
```

Los argumentos pasados a este script son pasados a su vez a `pytest`. Por ejemplo, para ejecutar un único test en concreto:

```sh
$ scripts/test src/test_abc.py::test_abc
```

Para mostrar la ayuda usar `--help` como argumento.

### Dependencias

Este proyecto usa [pip-compile](https://github.com/jazzband/pip-tools) para gestionar las dependencias de Python:

* `requirements.in` - listado de dependencias de la app
* `requirements.txt` - fichero auto-generado con las versiones fijadas (pinned) tanto de dependencias directas, como transitivas (dependencias de dependencias)

Ejecutar siempre `scripts/compile-deps` después de modificar las dependencias de `requirements.in` para producir un nuevo `requirements.txt`.

```sh
$ scripts/compile-deps | tee requirements.txt
... puede tardar unos minutos ...
```

Al compilar o empaquetar la app, Docker lanzará automáticamente `pip install -r requirements.txt` para construir el virtualenv de la app

Acordarse de actualizar el venv de `D:\Venv\<proyecto>` con:
```
(proyecto) C:\Windows>pip install -r \\wsl$\Ubuntu\home\<user>\Kapri2API\requirements.txt
```

### Archivos de configuración

En la carpeta `config` se encuentra el archivo `Kapri2API.conf` que deberá copiarse al directorio `etc` de la 
instalación final. Este fichero contiene los valores de release.
Al arrancar el servicio deberemos especificar el parámetro `--config /etc/Kapri2API.conf`.

Para ejecutar el programa en el entorno de desarrollo, crear el archivo `Kapri2API_default.conf` con el contenido
deseado y ubicarlo en la carpeta `config`. Luego arrancar el programa sin especificar `--config`.

### Directori d'imatges

A la instal·lació final caldrà crear el directori `/etc/imgrepo`
i popular-lo amb les imatges llistades a `GlobalConsts` sota la key `'const_images_excluded_names_to_remove'`.

A l'entorn de desenvolupament caldrà crear el directori `imgrepo`.

### Base de dades

A la instal·lació final, la base de dades sqlite apareixerà amb el nom `kapridb.sqlite` al directori `/etc`

A l'entorn de desenvolupament caldrà crear el directori `instance`. Allí apareixerà la base de dades.

### Modes de funcionament

El servei Kapri2API es basa en una app de Flask, i disposa de tres modes d'arrencada controlats per la variable 
d'entorn `APP_MODE`.

* Si `APP_MODE` no està definida o val 'normal', el servei arrenca el waitress. i tindrem un servidor API. 
En aquest mode, l'aplicació admet l'argument '-c'/'--config' per especificar el nom de l'arxiu de configuració.
Si no s'especifica, treballarà amb l'arxiu de configuració per defecte `config/Kapri2API_default.conf`.
Aquest és el mode de funcionament en release i en desenvolupament quan fem `debug_on_pc`.

* Si `APP_MODE` val 'maintenance', llavors el servei arrenca l'aplicació `cli` prenent l'arxiu de configuració per 
defecte `config/Kapri2API_default.conf`. D'aquesta manera admet les comandes en línia pròpies de l'aplicació flask. 
En concret, les més útils són:
  * `--help`
  * `db --help`
  * `db init`
  * `db migrate -m nom_de_la_versió`
  * `db upgrade`
Tenir present que en aquest mode, kapri_app.py s'instancia però no s'arrenca (no fa l'start). Tampoc arrenca els schedulers.

* Si `APP_MODE` val 'test':
  * L'aplicació pren la configuració de test interna.
  * No s'arrenca (no fa l'start) de kapri_app ni schedulers.
  * Treballa amb una base de dades en RAM.
Per tant, serveix per fer testejar algunes rutines aïlladament.

A `README_run_configurations.md` s'expliquen les configuracions de run/debug necessàries per arrencar l'aplicació en
els diferents modes i com fer el manteniment de la base de dades.

### Migracions:
Per crear un nou arxiu de versions de la base de dades, a l'entorn local, seguir aquests passos:

  * esborrar la base de dades sqlite del directori instance
  * Executar la comanda upgrade, per crear la base de dades i deixar-la en l'estat de la darrera versió migrada.
  * Executar la comanda migrate.
  * Editar l'arxiu de versions i afegir-hi les comandes personalitzades a l'apartat `# ### Customized commands ###`

### Modificació d'una taula existent des d'un arxiu versions

Per modificar una taula existent des de l'arxiu de versions, cal en primer lloc afegir el següent import:

````
from sqlalchemy import Table, MetaData
````

Després, a la secció `Customized commands` cal posar el codi que modificarà la taula. El següent exemple mostra com inserir
un nou registre a la taula `images`:

```markdown

    # ### Customized commands ###

    # Create a metadata object
    metadata = MetaData()

    # Use the metadata to reflect the existing database
    metadata.reflect(bind=op.get_bind())

    # Access the 'images' table using the metadata
    table_images = Table('images', metadata, autoload=True, autoload_with=op.get_bind())

    # Perform the bulk insert with the retrieved table object
    op.bulk_insert(
        table_images,
        [
            {
                'image_id': GlobalConsts.get('const_display_img_icon_example_id'),
                'customer_id': None,
                'name': GlobalConsts.get('const_display_img_icon_example_name'),
                'parameter': GlobalConsts.get('const_display_img_icon_example_parameter'),
                'imgext': GlobalConsts.get('const_display_img_icon_example_imgext'),
                'imgb64': GlobalConsts.get('const_display_img_icon_example_b64').encode(),
                'datetimestamp': datetime.utcnow(),
            },
        ],
    )

    # ### end Customized commands ###


```
