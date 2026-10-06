# Notes sobre l'organització del software.

## El tractament de les apis

### La url /let_me_know_instruction
El terminal Kapri rep les crides procedents dels diferents canals exteriors (cloud, http, json, ktp) a través de
la url `'/let_me_know_instruction'` el comportament de la qual l'implementa la classe `LetMeKnowInstruction`.
Però qui veritablement discerneix la instrucció concreta és la classe `LetMeKnowProcess`. 

Aquesta classe processa les instruccions de tres maneres diferents. Vejam un exemple de cada cas:

* `'ins_cpu_test_node_link'`: en aquest cas la instrucció es processa íntegrament al `LetMeKnowProcess`, ja que el resultat és immediat.
* `'ins_mifare_key_write'`: en aquest cas, també es processa íntegrament, però requereix d'una crida al `KxpHostProAPI`, 
que es farà sempre via `PostWoman`. De fet, en tot el codi, les crides http se centralitzen a través de `PostWoman`.
* `'ins_screen_image_store'`: en aquest cas la instrucció es processa mitjançant una instància d'un objecte del kapri_app.
En aquest exemple és kapri_app.mgr_images.store() qui ho resol.

La url `'/let_me_know_instruction'`, a banda de rebre crides dels canals exteriors, també rep crides fetes pel mòdul semioffline.
Així és com processa els batch d'instruccions. La classe `MgrSemiOfflineApiCaller` és la que s'encarrega de fer aquest "autocall".

I també rep les crides de les instruccions rebudes en els batchs de resposta del cloud. En aquest cas, és el procediment
`autocall_let_me_know()` del mòdul `MgrCloudTerminal` l'encarregat de fer l'"autocall".

## Les url de suport al KapriWebAdminjs
La resta de urls donen suport al KapriWebAdminjs. Moltes són específiques de la interficie web, com ara `'/Users/Login'`.
Altres, permeten que el KapriWebAdminjs pugui fer operacions similars a les que poden fer les instruccions rebudes pels 
canals externs. En aquest cas, per no repetir codi es poden seguir diverses estratègies. Vejam un exemple de cadascuna:

* `'/screen_images_store'`: Aquesta url té el mateix efecte que la instrucció `'ins_screen_image_store'`. Per això,
la classe `ScreenImagesStore` encarregada de definir el seu comportament processa la tasca a través de la instància
self.kapri_app.mgr_images.store() del kapri_app. Exactament igual a com ho fa el mòdul `LetMeKnowProcess` per tractar 
la instrucció equivalent.

* `'/assistwritemifarekey'`: Aquesta url té el mateix efecte que la instrucció `'ins_mifare_key_write'`. Com que aquesta 
instrucció es tracta íntegrament al `LetMeKnowProcess`, la solució adoptada a la classe `AssistWriteMifareKeys` encarregada
de definir el seu comportament consisteix en fer una "autocall" a la url `'/let_me_know_instruction'` passant-li la 
instrucció equivalent. En aquest cas, per fer l'"autocall" usarem la classe `MgrSemiOfflineApiCaller`.



