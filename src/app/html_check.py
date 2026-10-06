# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import re
import base64
import inspect
from PIL import Image
import io
import logging


class HtmlCheck:

    @staticmethod
    def check(s_html):
        try:
            '''
            0.- Vigilar que s_html pot ser None
    
            1.- Eliminarem del string s_html tots els caracters ascii  amd valor decimal per sota de 32. El primer caracter que admetem és l'espai en blanc, ascii 32 decimal
    
            2.- Ho passarem tot a lowercase per detectar les substrings perilloses.
    
            3.- No permetrem EventHandlers. Els casos que tractarem seran ( https://owasp.org/www-community/xss-filter-evasion-cheatsheet ) :
                FSCommand, onAbort, onActivate, onAfterPrint, onAfterUpdate, onBeforeActivate, onBeforeCopy, onBeforeCut, onBeforeDeactivate, onBeforeEditFocus, onBeforePaste, onBeforePrint, onBeforeUnload, onBeforeUpdate, onBegin, onBlur, onBounce, onCellChange, onChange, onClick, onContextMenu, onControlSelect, onCopy, onCut, onDataAvailable, onDataSetChanged, onDataSetComplete, onDblClick, onDeactivate, onDrag, onDragEnd, onDragLeave, onDragEnter, onDragOver, onDragDrop, onDragStart, onDrop, onEnd, onError, onErrorUpdate, onFilterChange, onFinish, onFocus, onFocusIn, onFocusOut, onHashChange, onHelp, onInput, onKeyDown, onKeyPress, onKeyUp, onLayoutComplete, onLoad, onLoseCapture, onMediaComplete, onMediaError, onMessage, onMouseDown, onMouseEnter, onMouseLeave, onMouseMove, onMouseOut, onMouseOver, onMouseUp, onMouseWheel, onMove, onMoveEnd, onMoveStart, onOffline, onOnline, onOutOfSync, onPaste, onPause, onPopState, onProgress, onPropertyChange, onReadyStateChange, onRedo, onRepeat, onReset, onResize, onResizeEnd, onResizeStart, onResume, onReverse, onRowsEnter, onRowExit, onRowDelete, onRowInserted, onScroll, onSeek, onSelect, onSelectionChange, onSelectStart, onStart, onStop, onStorage, onSyncRestored, onSubmit, onTimeError, onTrackChange, onUndo, onUnload, onURLFlip, seekSegmentTime
            4.- No permetrem seqüencies com:
                5.1- &#
                5.2- "&
                5.3- /*
                5.4- */
                5.5- <!--
                5.6- -->
                5.7- \[0-9][a-z]   Backslash seguit de qualsevol caracter del "0" al "9" o de la "a" a la "f"
                5.8 base64
            5.- Borrem aquestes paraules per tal de permetre-les( https://www.thefreedictionary.com/words-that-end-in-script ):
                nondescript(mediocre),  superscript(sobreescrito),
                manuscript(manuscrito), transcript(transcripción), postscript(posdata), typescript(mecanografiado)
                subscript(subíndice), conscript(reclutar), prescript(precepto)
                rescript(edicto), adscript(adscrito)
    
                No permetrem el substring script si redera no té una lletra de la "a" a la "z". Volem permetre paraules com "escriptor", "escriptura"
                
            6.- Validem imatges base64. El número de vegades que apareix la paraula base64 ha de ser el mateix que el número de grups "<img src="data:image/xxx;base64 ..."
                Cada block base64 es chequeixa per comprobar que sigui una imatge vàlida
    
            '''
            if s_html is None:
                return False
            # --1-- caracters ascii  amd valor decimal per sota de 32
            # Fem servir el comando sub de la regular expression: tot lo que no estigui entre l'espai i la tilde queda eliminat
            new_s_html = re.sub("[^ -~]+", "", s_html)

            # -- 2 -- Lowercase
            new_s_lower = new_s_html.lower()

            # -- 3 -- No permetrem EventHandlers
            forbidden_l = ['fscommand', 'onabort', 'onactivate', 'onafterprint', 'onafterupdate', 'onbeforeactivate', 'onbeforecopy', 'onbeforecut', 'onbeforedeactivate', 'onbeforeeditfocus', 'onbeforepaste', 'onbeforeprint', 'onbeforeunload', 'onbeforeupdate', 'onbegin', 'onblur', 'onbounce', 'oncellchange', 'onchange', 'onclick', 'oncontextmenu', 'oncontrolselect', 'oncopy', 'oncut', 'ondataavailable', 'ondatasetchanged', 'ondatasetcomplete', 'ondblclick', 'ondeactivate', 'ondrag', 'ondragend', 'ondragleave', 'ondragenter', 'ondragover', 'ondragdrop', 'ondragstart', 'ondrop', 'onend', 'onerror', 'onerrorupdate', 'onfilterchange', 'onfinish', 'onfocus', 'onfocusin', 'onfocusout', 'onhashchange', 'onhelp', 'oninput', 'onkeydown', 'onkeypress', 'onkeyup', 'onlayoutcomplete', 'onload', 'onlosecapture', 'onmediacomplete', 'onmediaerror', 'onmessage', 'onmousedown', 'onmouseenter', 'onmouseleave', 'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup', 'onmousewheel', 'onmove', 'onmoveend', 'onmovestart', 'onoffline', 'ononline', 'onoutofsync', 'onpaste', 'onpause', 'onpopstate', 'onprogress', 'onpropertychange', 'onreadystatechange', 'onredo', 'onrepeat', 'onreset', 'onresize', 'onresizeend', 'onresizestart', 'onresume', 'onreverse', 'onrowsenter', 'onrowexit', 'onrowdelete', 'onrowinserted', 'onscroll', 'onseek', 'onselect', 'onselectionchange', 'onselectstart', 'onstart', 'onstop', 'onstorage', 'onsyncrestored', 'onsubmit', 'ontimeerror', 'ontrackchange', 'onundo', 'onunload', 'onurlflip', 'seeksegmenttime']
            for forb in forbidden_l:
                if forb in new_s_lower:
                    return False

            # -- 4 -- No permetrem certes seqüencies
            forbidden_l = ['&#', '"&', '/*', '*/', '<!--', '-->']
            for forb in forbidden_l:
                if forb in new_s_lower:
                    return False
            # --  No permetem \[0-9][a-z]   Backslash seguit de qualsevol caracter del "0" al "9" o de la "a" a la "f"
            if re.search("\\\\[0-9a-f]", new_s_lower) is not None:
                return False

            # -- 5 -- substring script
            #  Permetem nondescript, superscript, manuscript, transcript, postscript, typescript, subscript, conscript, prescript, rescript, adscript
            allowed_l = ['nondescript', 'superscript', 'manuscript', 'transcript', 'postscript', 'typescript', 'subscript', 'conscript', 'prescript', 'rescript', 'adscript']
            s_filtered = re.sub(r'|'.join(map(re.escape, allowed_l)), '', new_s_lower)
            # No permetrem el substring script si redera no té una lletra de la "a" a la "z"
            if re.search("script[^a-z]", s_filtered) is not None:
                return False

            # -- 6 -- Chequeixem imatges base64
            # -- el número de vegades que apareix la paraula base64 ha de ser el mateix que el número de grups "data:image/xxx;base64 ..."
            uc_base64_times = new_s_lower.count('base64')
            ll_matches = re.findall('data:image\/[^;]+;base64[^"]+"', new_s_html)
            if len(ll_matches) != uc_base64_times:
                return False
            for match in ll_matches:
                try:
                    match = match.replace(' ', '')
                    sImgB64 = match.split('base64,')[1].strip()
                    bImgB64 = sImgB64.encode()
                    binimage = base64.b64decode(bImgB64)
                    # Validem que sigui imatge correcta
                    with io.BytesIO(binimage) as buffer:
                        with Image.open(buffer) as ImgCandidate:
                            bValidImage = True
                except IOError as ioe:
                    logging.debug(
                        f'{inspect.stack()[0][3]} Exception: {str(ioe)} (called by: {inspect.stack()[1][3]})')
                    return False
                except Exception as e:
                    logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
                    return False
            return True
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')
            return False
