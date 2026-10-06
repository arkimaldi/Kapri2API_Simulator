# OPTSEL — Document Intern de Disseny de Firmware

**Kapri2 · Kimaldi · Versió: maig 2026**

---

## 1. Propòsit del mòdul

El mòdul OPTSEL permet al servidor cloud presentar a l'usuari una llista d'opcions personalitzada i obtenir-ne la selecció. A diferència del KYB-MGR, que gestiona una llista global i permanent configurada al terminal, l'OPTSEL activa una interacció puntual per a cada usuari. És genèric: pot usar-se per a motiu de fitxatge, projecte, centre de cost, motiu de visita, etc.

---

## 2. Paràmetres de la instrucció `ins_optsel_run`

### 2.1 `options` (obligatori)

Array d'entre 1 i 100 elements. Ha de contenir almenys un element seleccionable. El servidor l'envia ja ordenat; el terminal conserva l'ordre rebut.

Cada element pot tenir els camps següents:

| Camp | Obligatori | Seleccionable | Notes |
|---|---|---|---|
| `code` | Sí | Sí | Dígits `"0"`–`"9"`, longitud 1–8. **Únic per element.** Si és `null`/absent → títol de secció. |
| `label` | Sí | Tots | Text pantalla, 1–25 caràcters. |
| `ref` | No | Sí (només) | Alfanumèric opac, 1–64 caràcters. Retornat a l'event. No mostrat a pantalla. Unicitat responsabilitat del servidor. |
| `color` | No | Tots | Color del text. Valors CSS o hex compatibles amb el renderer. |
| `style` | No | Tots | Array d'estils tipogràfics: `"bold"`, `"underline"`. |

### 2.2 Regles de coherència de `options`

- Si `code` és `null` o absent → element no seleccionable (títol de secció).
- Si `code` és `null` o absent → `ref` ha de ser `null` o absent. Si no, rebutjar amb `RET_INVALIDARGUMENT`.
- **Si la llista conté algun títol de secció, el primer element ha de ser un títol.** Si no, `RET_INVALIDARGUMENT`.
- **Cada títol ha d'anar seguit d'almenys un element seleccionable.** No es permeten seccions buides. Si no, `RET_INVALIDARGUMENT`.
- La llista ha de tenir almenys un element seleccionable global. Si no, `RET_INVALIDARGUMENT`.
- **Si `code` està definit i no és `null`, ha de ser únic per a cada element.** Dos elements amb el mateix `code` caurien ambigüitat al filtratge i a la selecció. Si no, `RET_INVALIDARGUMENT`.
- `default_code` ha de coincidir amb el `code` d'un element seleccionable (no d'un títol). Si no, `RET_INVALIDARGUMENT`.
- `code` ha de ser exclusivament dígits `"0"`–`"9"`. Qualsevol altre caràcter → `RET_INVALIDARGUMENT`.
- La unicitat de `ref` **no** és una restricció del terminal. El terminal no interpreta `ref`; és responsabilitat del servidor garantir-ne la unicitat si la seva lògica ho requereix.

### 2.3 `default_code` (opcional)

Codi de l'opció seleccionable que apareix preseleccionada en activar-se el mòdul. Si s'omet, es preselecciona la primera opció seleccionable.

### 2.4 `show_code` (opcional, per defecte `true`)

Indica si el camp `code` de cada opció seleccionable es mostra a pantalla al costat del `label`.

- Si `true`: cada línia mostra `[code] - [label]`.
- Si `false`: cada línia mostra només `[label]` aprofitant tota l'amplada de pantalla.
- El filtratge per teclat numèric funciona igual en tots dos casos.

### 2.5 `theme` (opcional, per defecte `"light"`)

Defineix l'esquema de colors de la interfície de selecció.

- `"light"`: fons blanc, element seleccionat en highlight contrastat fosc (`#1a73e8`).
- `"dark"`: fons gris fosc (`#1e2a30`), element seleccionat en highlight contrastat clar (blanc).
- Qualsevol altre valor → `RET_INVALIDARGUMENT`.

### 2.6 `key_beep` (opcional, per defecte `true`)

Habilita el feedback acústic del teclat durant la interacció.

- Si `true`: cada pulsació efectiva emet un pitit curt (`'1-beep'`).
- Si `true`: una pulsació no efectiva (dígit que no produeix cap resultat en mode filtrat) emet tres pitits d'error (`'3-beeps'`).
- Si `false`: cap feedback acústic de teclat. Els tres pitits per lectura de targeta ignorada es mantenen **sempre**, independentment d'aquest paràmetre.

### 2.7 `keyboard_timeout` (opcional, per defecte 5)

Temps màxim d'inactivitat en segons. Rang 1–10.

- El timer es reinicia amb cada pulsació de tecla (dígit, fletxa, MENU).
- Si expira sense interacció → el mòdul envia `on_optsel_selection` amb `result = "timeout"`.
- El timeout **no** confirma automàticament l'opció preseleccionada. Només OK confirma.

---

## 3. Comportament de navegació al terminal

### 3.1 Estat inicial

En activar-se el mòdul, el terminal mostra la llista completa amb títols de secció (si n'hi ha), posicionat sobre l'opció `default_code` (o la primera seleccionable si no hi ha `default_code`). El `keyboard_timeout` comença a comptar.

### 3.2 Navegació amb fletxes

- Les fletxes amunt/avall naveguen opció a opció per totes les opcions seleccionables.
- Els títols de secció es mostren però es salten (no són seleccionables). El cursor **no** s'atura sobre un títol.
- La llista **NO** és circular: arribar al final o al principi no fa res.
- Cada pulsació de fletxa reinicia el `keyboard_timeout`.
- Si `key_beep` és `true`, cada pulsació de fletxa efectiva emet un pitit curt.

### 3.3 Mode filtrat (filtratge progressiu per teclat numèric)

S'activa quan l'usuari prem qualsevol dígit (0–9).

- Cada dígit afegit estreny el filtre: es mostren només les opcions seleccionables el `code` de les quals comença per la seqüència teclejada.
- En mode filtrat, els títols de secció **no** es mostren. La llista filtrada és plana.
- Si un dígit no produeix cap resultat (cap opció comença per la nova seqüència), el dígit s'ignora, el filtre no canvia, i si `key_beep` és `true` s'emeten tres pitits d'error.
- Si el filtre deixa exactament una opció, l'usuari ha de prémer OK igualment. **No hi ha confirmació automàtica.**
- Cada dígit teclejat efectiu reinicia el `keyboard_timeout`.

> **Exemple:** llista amb 01-Entrada, 02-Sortida, 10-Inici pausa, 11-Fi pausa.
> L'usuari prem `0` → es mostren 01 i 02. Prem `1` → es mostra només 01. Prem OK → confirma 01.

### 3.4 Tecla MENU (antiga BACK, reserigrafada)

- **En mode filtrat:** neteja el filtre i torna a l'estat inicial (llista completa amb títols, cursor sobre `default_code`). Reinicia el `keyboard_timeout`.
- **Fora de mode filtrat, si la llista té títols de secció:** salta al títol de secció següent i posiciona el cursor sobre la primera opció seleccionable d'aquella secció. Comportament circular: des de l'última secció torna a la primera.
- **Fora de mode filtrat, si la llista no té títols:** pagina de `LINES_PER_PAGE` en `LINES_PER_PAGE`.
- En tots els casos, reinicia el `keyboard_timeout`.

### 3.5 Tecla OK

- Confirma l'opció actualment seleccionada (la que té el cursor).
- Envia l'event `on_optsel_selection` amb `result = "confirmed"` i `selected_option` amb els camps `code`, `label` i `ref` (si existia).
- El mòdul es desactiva.

### 3.6 Timeout

- Si el `keyboard_timeout` expira sense cap interacció, el mòdul envia `on_optsel_selection` amb `result = "timeout"` i es desactiva.
- No es confirma cap opció automàticament.

### 3.7 Noves lectures durant la interacció

- Qualsevol lectura de targeta o QR mentre el mòdul és actiu és ignorada.
- No genera cap POST.
- Provoca tres pitits d'error (independentment del valor de `key_beep`).

---

## 4. Lògica de pantalla (`_show_full_list`)

El títol de la secció activa es mostra sempre a la **primera línia** (fix). Les `LINES_PER_PAGE - 1` línies restants mostren els seleccionables de la secció paginats per posició del cursor dins la secció. Si hi ha línies lliures, s'aprofiten per mostrar el títol i els primers seleccionables de la secció següent, **però mai un títol sol a l'última línia sense cap seleccionable sota**.

Si la llista no té títols, paginació simple per seleccionables (`LINES_PER_PAGE` línies).

`LINES_PER_PAGE` = **6** (valor actual, ajustable com a constant de classe).

### Exemple visual (LINES_PER_PAGE = 6, 2 seccions × 2 opcions)

```
cursor = 01:          cursor = 10:
──────────────        ──────────────
Entrades              Pausas
▶ 01 - Entrada        ▶ 10 - Inici pausa
  02 - Sortida          11 - Fi pausa
Pausas
  10 - Inici pausa
  11 - Fi pausa
```

---

## 5. Event `on_optsel_selection`

Sempre s'envia un event final, tant si l'usuari ha confirmat com si ha expirat el timeout.

- **`result = "confirmed"`**: `selected_option` conté `code`, `label` i `ref` (si existia). El camp `msgId` es retorna si estava present a la instrucció.
- **`result = "timeout"`**: `selected_option` absent. `msgId` es retorna si estava present.

Després d'enviar l'event, el terminal queda a l'espera de noves instruccions del servidor. El servidor és responsable de restaurar la pantalla.

---

## 6. Incompatibilitats i rebuig de la instrucció

| Condició | Resposta |
|---|---|
| Mòdul KYB-MGR actiu | `ins_optsel_run` → `RET_FAILED` |
| Mòdul OPTSEL ja actiu | `ins_optsel_run` → `RET_FAILED` |

---

## 7. `msgId`

- El terminal no interpreta ni valida el contingut de `msgId`. És opac.
- El retorna literalment a l'ACK de la instrucció (`ans_optsel_run`) i a l'event posterior (`on_optsel_selection`).
- Ha de ser únic per interacció. Longitud màxima recomanada: 64 caràcters.
- El paràmetre s'accepta tant com `msgId` com `msg_id` (les dues grafies).

---

## 8. Taula resum de paràmetres de `ins_optsel_run`

| Paràmetre | Obligatori | Per defecte | Notes |
|---|---|---|---|
| `options` | Sí | — | Array 1–100 elements, mínim 1 seleccionable. Codes únics. Seccions no buides. |
| `default_code` | No | 1a opció sel. | Ha de ser `code` d'un element seleccionable. |
| `show_code` | No | `true` | `false` → amaga el `code`, aprofita amplada pantalla. |
| `theme` | No | `"light"` | `"light"` o `"dark"`. Altres valors → `RET_INVALIDARGUMENT`. |
| `key_beep` | No | `true` | `false` → silencia feedback acústic del teclat. |
| `keyboard_timeout` | No | `5` | Rang 1–10 segons. Es reinicia a cada pulsació. |

---

## 9. Decisions tancades

- Llista **NO** circular (fletxes).
- Navegació MENU entre seccions: **sí** circular (torna a la primera secció des de l'última).
- El timeout **NO** confirma automàticament cap opció.
- En mode filtrat, els títols de secció **no** es mostren.
- Si el filtre deixa una única opció, cal OK igualment.
- `show_code` per defecte és `true`.
- `keyboard_timeout` per defecte és 5 segons.
- `theme` per defecte és `"light"`.
- `key_beep` per defecte és `true`. Afecta el teclat; els tres pitits per targeta ignorada es mantenen sempre.
- La tecla BACK ha estat reserigrafada com a MENU/paginació (`'B'` → `'MENU'`). **No s'usa per cancel·lar.** L'única sortida és OK o timeout.
- Si la llista conté títols, el primer element ha de ser un títol.
- **Seccions buides no permeses** (cada títol ha d'anar seguit d'almenys un seleccionable).
- Una instrucció `ins_optsel_run` rebuda mentre el mòdul ja està actiu és rebutjada amb `RET_FAILED`.
- El camp `style` (anteriorment `type`) conté estils tipogràfics: `"bold"`, `"underline"`. S'aplica també a títols de secció però el cursor no s'hi atura.
- El `code` ha de ser únic per element seleccionable. La unicitat de `ref` és responsabilitat del servidor.
- `LINES_PER_PAGE` = 6 (valor actual ajustat a la pantalla del Kapri2).
