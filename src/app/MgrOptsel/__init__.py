# (C) 2025 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import threading
import queue
import inspect
import logging

from app.ktp_ret import KtpRet
from app.MgrOptsel.k_timer import KTimer
from app.MgrOptsel.k_check import KCheck


class MgrOptsel:
    """
    Mòdul OPTSEL — Selecció d'opcions personalitzada per usuari.

    Activat per la instrucció ins_optsel_run.
    El mòdul mostra una llista d'opcions a pantalla, permet navegar-hi
    amb les tecles de menu, fletxa i teclat numèric, i retorna la selecció
    de l'usuari mitjançant l'event on_optsel_selection.

    Vegeu el document intern de disseny de firmware per al comportament
    detallat de navegació, filtratge progressiu i tecla MENU.
    """

    # ── constants ──────────────────────────────────────────────────────────────
    QUEUE_BRET_TIMEOUT      = 5

    OPTIONS_MIN             = 1
    OPTIONS_MAX             = 100
    CODE_LEN_MIN            = 1
    CODE_LEN_MAX            = 8
    LABEL_LEN_MIN           = 1
    LABEL_LEN_MAX           = 25
    REF_LEN_MIN             = 1
    REF_LEN_MAX             = 64

    BUTTON_B_ACTION_LIST = ['menu', 'cancel']
    BUTTON_B_ACTION_DEFAULT = 'menu'

    KEYBOARD_TIMEOUT_MIN    = 1
    KEYBOARD_TIMEOUT_MAX    = 10
    KEYBOARD_TIMEOUT_DEFAULT = 5

    THEME_LIST              = ['light', 'dark']
    THEME_DEFAULT           = 'light'

    STYLE_VALID             = {'bold', 'underline'}

    LINES_PER_PAGE          = 6

    # colors de tema (dark/light) per a la pantalla de llista
    THEME_STYLES = {
        'light': {
            'bg':        'white',
            'fg':        'black',
            'hl_bg':     '#1a73e8',
            'hl_fg':     'white',
        },
        'dark': {
            'bg':        '#1e2a30',
            'fg':        'white',
            'hl_bg':     'white',
            'hl_fg':     '#1e2a30',
        },
    }

    def __init__(self, app, mgr_guispy, buzzer_fp, on_optsel_selection_cb):
        """
        Paràmetres
        ----------
        app                           : referència a l'aplicació principal (kapri_app)
        mgr_guispy                    : objecte amb el mètode write_screen_html per escriure a pantalla
        buzzer_fp                     : funció sense arguments per activar el buzzer (un pip curt).
                                        El mòdul la cridarà per cada pulsació efectiva (key_beep=True)
                                        i tres vegades per pulsació no efectiva.
        on_optsel_selection_cb : callable(msg_arg) que el mòdul cridarà per publicar
                                        l'event on_optsel_selection quan la interacció finalitza
                                        (confirmed o timeout). msg_arg tindrà la forma:
                                        {
                                            'msgId': ...,            # si estava present a la instrucció
                                            'result': 'confirmed' | 'timeout',
                                            'selected_option': {     # només si result = 'confirmed'
                                                'code':  ...,
                                                'label': ...,
                                                'ref':   ...         # només si estava present a l'opció
                                            }
                                        }
        """
        try:
            self.app                            = app
            self.mgr_guispy                     = mgr_guispy
            self.buzzer_fp                      = buzzer_fp
            self.on_optsel_selection_cb  = on_optsel_selection_cb

            # cues
            self.incoming_events_queue  = queue.Queue()
            self.run_bret_queue         = queue.Queue()

            # timer de inactivitat de teclat
            self.keyboard_timer = KTimer(self.on_keyboard_timer)
            self.keyboard_timer.clear_tmo()
            self.incoming_events_queue.queue.clear()
            self.run_bret_queue.queue.clear()

            # estat de la sessió activa (None = mòdul inactiu)
            self._session = None  # dict amb tots els paràmetres validats de la sessió activa

            # fil principal
            self.main_thread = None

        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} '
                          f'(called by: {inspect.stack()[1][3]})')

    # ── arrencada ──────────────────────────────────────────────────────────────

    def start(self):
        """Arrenca el fil principal del mòdul. Cridar una sola vegada en inicialitzar."""
        self.main_thread = threading.Thread(target=self.main_thread_task, daemon=True)
        self.main_thread.start()

    # ── API pública ────────────────────────────────────────────────────────────

    def is_running(self):
        """
        Retorna True si el mòdul té una sessió activa (ins_optsel_run en curs).
        Usar per rebutjar events de GUI mentre el mòdul està actiu.
        """
        return self._session is not None

    def run(self, msg_arg):
        """
        Handler de la instrucció ins_optsel_run.

        Fa el parse i validació de msg_arg, i si tot és correcte activa el mòdul.
        Retorna ucRet (int) de forma síncrona.

        Paràmetres
        ----------
        msg_arg : dict amb els arguments de la instrucció (options, default_code,
                  show_code, theme, theme_style_bg, theme_style_fg, theme_style_hl_bg, theme_style_hl_fg, key_beep,
                  keyboard_timeout, msgId).
        """
        try:
            session = self._parse_and_validate(msg_arg)
        except Exception:
            return KtpRet.RET_INVALIDARGUMENT

        self.on_incoming_event({'msgType': 'on_optsel_run', 'msgArg': {'session': session}})
        b_ret = self.run_bret_queue.get(block=True, timeout=MgrOptsel.QUEUE_BRET_TIMEOUT)
        if b_ret:
            return KtpRet.RET_OK
        else:
            return KtpRet.RET_FAILED

    def on_key_received(self, s_key):
        """Informa el mòdul d'una pulsació de tecla."""
        self.on_incoming_event({'msgType': 'on_keyboard_echo', 'msgArg': {'sKey': s_key}})

    # ── events interns ─────────────────────────────────────────────────────────

    def on_keyboard_timer(self):
        self.on_incoming_event({'msgType': 'on_keyboard_timeout', 'msgArg': {}})

    def on_incoming_event(self, event):
        try:
            self.incoming_events_queue.put(event)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} '
                          f'(called by: {inspect.stack()[1][3]})')

    # ── fil principal ──────────────────────────────────────────────────────────

    def main_thread_task(self):
        while True:
            try:
                event = self.incoming_events_queue.get()
                self.state_machine(event)
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} '
                              f'(called by: {inspect.stack()[1][3]})')

    # ── màquina d'estats ───────────────────────────────────────────────────────

    def state_machine(self, event_in):
        try:
            msg_type = event_in['msgType']
            msg_arg  = event_in['msgArg']

            if msg_type == 'on_optsel_run':
                self._do_run(msg_arg['session'])

            elif msg_type == 'on_keyboard_timeout':
                if self._session is not None:
                    key_beep = self._session.get('key_beep', True)
                    if key_beep:
                        self._beep('3-beeps')
                    self._finish('timeout')

            elif msg_type == 'on_keyboard_echo':
                if self._session is not None:
                    self._handle_key(msg_arg['sKey'])

        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} '
                          f'(called by: {inspect.stack()[1][3]})')

    # ── lògica de sessió ───────────────────────────────────────────────────────

    def _do_run(self, session):
        """Activa una nova sessió. Si el mòdul ja estava actiu, rebutja."""
        if self._session is not None:
            self.run_bret_queue.put(False)
            return

        self._session = session
        self._session['filter_digits'] = None          # seqüència de dígits filtrada activa
        self._session['visible_items'] = list(         # llista d'ítems visibles (índexs a options)
            self._selectable_indices(session)
        )
        # posicionar cursor sobre default_code
        default_code = session.get('default_code')
        sel_items = self._selectable_items(session)
        if default_code and any(it['code'] == default_code for it in sel_items):
            self._session['cursor_code'] = default_code
        else:
            first = sel_items[0] if sel_items else None
            self._session['cursor_code'] = first['code'] if first else None

        self.run_bret_queue.put(True)
        self._reset_timer()
        self._show_screen()

    def _handle_key(self, s_key):
        s_key_name = self._decode_key(s_key)
        session = self._session
        key_beep = session.get('key_beep', True)

        if s_key_name == 'OK':
            # confirmar selecció actual
            if key_beep:
                self._beep('1-beep')
            self._finish('confirmed')

        elif s_key_name == 'UP':
            moved = self._move_cursor(-1)
            if moved and key_beep:
                self._beep('1-beep')
            self._reset_timer()
            self._show_screen()

        elif s_key_name == 'DOWN':
            moved = self._move_cursor(1)
            if moved and key_beep:
                self._beep('1-beep')
            self._reset_timer()
            self._show_screen()

        elif s_key_name == 'MENU':
            if session['button_b_action'] == 'cancel':
                if key_beep:
                    self._beep('1-beep')
                self._finish('cancelled')
            else:
                if session['filter_digits'] is not None:
                    # mode filtrat → netejar filtre i tornar a l'estat inicial
                    self._clear_filter()
                else:
                    # navegar per seccions o paginar
                    self._menu_navigate()
                if key_beep:
                    self._beep('1-beep')
                self._reset_timer()
                self._show_screen()

        elif s_key_name in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            effective = self._apply_digit_filter(s_key_name)
            if effective:
                if key_beep:
                    self._beep('1-beep')
            else:
                if key_beep:
                    self._beep('3-beeps')
            self._reset_timer()
            self._show_screen()

        # altres tecles: ignorades silenciosament

    def _finish(self, result):
        """Tanca la sessió i envia l'event on_optsel_selection."""
        self.keyboard_timer.clear_tmo()
        session = self._session
        self._session = None

        msg_arg = {'result': result}

        # propagar msgId si estava present
        if 'msg_id' in session and session['msg_id'] is not None:
            msg_arg['msgId'] = session['msg_id']

        if result == 'confirmed':
            cursor_code = session.get('cursor_code')
            # trobar l'opció seleccionada
            selected = next(
                (it for it in session['options'] if it.get('code') == cursor_code),
                None
            )
            if selected:
                sel_dict = {
                    'code':  selected['code'],
                    'label': selected['label'],
                }
                if 'ref' in selected and selected['ref'] is not None:
                    sel_dict['ref'] = selected['ref']
                msg_arg['selected_option'] = sel_dict

        try:
            self.on_optsel_selection_cb(msg_arg)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} on_optsel_selection_cb Exception: {str(e)}')

    # ── navegació ──────────────────────────────────────────────────────────────

    def _selectable_items(self, session=None):
        """Retorna la llista d'ítems seleccionables (amb code) de la sessió."""
        s = session or self._session
        return [it for it in s['options'] if it.get('code') is not None]

    def _selectable_indices(self, session=None):
        """Retorna els índexs (a options) dels ítems seleccionables."""
        s = session or self._session
        return [i for i, it in enumerate(s['options']) if it.get('code') is not None]

    def _visible_selectable_items(self):
        """
        Retorna la llista d'ítems seleccionables visibles (aplicant filtre si n'hi ha).
        En mode no filtrat: tots els seleccionables.
        En mode filtrat: els que el seu code comença per filter_digits.
        """
        session = self._session
        sel_items = self._selectable_items()
        fd = session.get('filter_digits')
        if fd:
            sel_items = [it for it in sel_items if it['code'].startswith(fd)]
        return sel_items

    def _move_cursor(self, delta):
        """
        Mou el cursor delta posicions (+1 avall, -1 amunt) entre els ítems visibles.
        Retorna True si s'ha mogut efectivament, False si ja era al límit.
        """
        session = self._session
        visible = self._visible_selectable_items()
        if not visible:
            return False
        codes = [it['code'] for it in visible]
        cursor = session.get('cursor_code')
        if cursor not in codes:
            session['cursor_code'] = codes[0]
            return True
        idx = codes.index(cursor)
        new_idx = max(0, min(len(codes) - 1, idx + delta))
        if new_idx == idx:
            return False
        session['cursor_code'] = codes[new_idx]
        return True

    def _clear_filter(self):
        """Neteja el filtre i torna al cursor sobre default_code."""
        session = self._session
        session['filter_digits'] = None
        default_code = session.get('default_code')
        sel_items = self._selectable_items()
        if default_code and any(it['code'] == default_code for it in sel_items):
            session['cursor_code'] = default_code
        else:
            session['cursor_code'] = sel_items[0]['code'] if sel_items else None

    def _menu_navigate(self):
        """
        Fora de mode filtrat: navegació per seccions (si hi ha títols)
        o paginació de LINES_PER_PAGE en LINES_PER_PAGE (si no n'hi ha).
        """
        session = self._session
        options = session['options']
        sel_items = self._selectable_items()
        codes = [it['code'] for it in sel_items]
        cursor = session.get('cursor_code')
        cursor_idx = codes.index(cursor) if cursor in codes else 0

        has_titles = any(it.get('code') is None for it in options)

        if has_titles:
            # trobar el pròxim títol després de la posició actual del cursor a options
            # La posició del cursor a options:
            cursor_pos_in_options = next(
                (i for i, it in enumerate(options)
                 if it.get('code') == cursor),
                0
            )
            # buscar el proper títol (code absent) a partir de cursor_pos_in_options+1
            next_title_pos = None
            for i in range(cursor_pos_in_options + 1, len(options)):
                if options[i].get('code') is None:
                    next_title_pos = i
                    break
            if next_title_pos is None:
                # wrap: tornar al primer títol
                for i in range(len(options)):
                    if options[i].get('code') is None:
                        next_title_pos = i
                        break
            if next_title_pos is not None:
                # primera opció seleccionable després d'aquest títol
                for i in range(next_title_pos + 1, len(options)):
                    if options[i].get('code') is not None:
                        session['cursor_code'] = options[i]['code']
                        return
        else:
            # paginació: saltar LINES_PER_PAGE posicions
            page, _ = divmod(cursor_idx, MgrOptsel.LINES_PER_PAGE)
            next_idx = (page + 1) * MgrOptsel.LINES_PER_PAGE
            if next_idx >= len(codes):
                next_idx = 0
            session['cursor_code'] = codes[next_idx]

    def _apply_digit_filter(self, digit):
        """
        Afegeix un dígit al filtre progressiu.
        Si el nou filtre no produeix cap resultat, ignora el dígit i retorna False.
        Si produeix resultats, actualitza el cursor si cal i retorna True.
        """
        session = self._session
        current_filter = session.get('filter_digits') or ''
        new_filter = current_filter + digit
        sel_items = self._selectable_items()
        filtered = [it for it in sel_items if it['code'].startswith(new_filter)]
        if not filtered:
            return False  # dígit ignorat
        session['filter_digits'] = new_filter
        # si el cursor actual no és al resultat filtrat, posicionar al primer
        cursor = session.get('cursor_code')
        if not any(it['code'] == cursor for it in filtered):
            session['cursor_code'] = filtered[0]['code']
        return True

    # ── pantalla ───────────────────────────────────────────────────────────────

    def _show_screen(self):
        session = self._session
        if session is None:
            return
        try:
            filter_digits = session.get('filter_digits')
            if filter_digits:
                self._show_filtered_list(filter_digits)
            else:
                self._show_full_list()
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} '
                          f'(called by: {inspect.stack()[1][3]})')

    def _show_full_list(self):
        """Mostra la llista completa amb títols de secció.

        El títol de la secció activa es mostra sempre a la primera línia (fix).
        Les LINES_PER_PAGE-1 línies restants mostren els seleccionables de la
        secció paginats. Si hi ha línies lliures, s'aprofiten per mostrar
        el títol i els primers seleccionables de la secció següent, sempre
        que el títol no quedi sol a l'última línia sense seleccionable sota.

        Si la llista no té títols, paginació simple per seleccionables.
        """
        session   = self._session
        options   = session['options']
        cursor    = session.get('cursor_code')
        show_code = session['show_code']
        ts = session['ts']

        has_titles = any(it.get('code') is None for it in options)

        if not has_titles:
            # sense títols: paginació simple per posició del cursor
            sel_items = self._selectable_items()
            sel_codes = [it['code'] for it in sel_items]
            cursor_idx = sel_codes.index(cursor) if cursor in sel_codes else 0
            page, _ = divmod(cursor_idx, MgrOptsel.LINES_PER_PAGE)
            page_start = page * MgrOptsel.LINES_PER_PAGE
            page_items = sel_items[page_start: page_start + MgrOptsel.LINES_PER_PAGE]
            lines_html = [
                self._render_item_html(it,
                    is_highlighted=(it.get('code') == cursor),
                    show_code=show_code, ts=ts, is_title=False)
                for it in page_items
            ]
            html = self._build_screen_html(lines_html, ts)
            self.mgr_guispy.write_screen_html(html)
            return

        # ── llista amb títols ──────────────────────────────────────────────────

        # 1. Trobar el títol actiu: l'últim títol que apareix abans del cursor
        active_title = None
        active_title_idx = None
        for i, it in enumerate(options):
            if it.get('code') is None:
                active_title = it
                active_title_idx = i
            elif it.get('code') == cursor:
                break

        # 2. Recollir els seleccionables de la secció activa
        #    (des del títol actiu fins al títol següent, excl.)
        section_start = active_title_idx if active_title_idx is not None else 0
        section_items = []
        for it in options[section_start:]:
            if it is active_title:
                continue
            if it.get('code') is None:
                break
            section_items.append(it)

        # 3. Paginar els seleccionables de la secció
        #    (disponible = LINES_PER_PAGE - 1 per al títol fix)
        available = MgrOptsel.LINES_PER_PAGE - 1 if active_title is not None else MgrOptsel.LINES_PER_PAGE
        sel_codes = [it['code'] for it in section_items]
        cursor_sec_idx = sel_codes.index(cursor) if cursor in sel_codes else 0
        page, _ = divmod(cursor_sec_idx, available)
        page_items = section_items[page * available: (page + 1) * available]

        # 4. Construir display: títol fix + ítems de la pàgina
        display = []
        if active_title is not None:
            display.append(active_title)
        display += page_items

        # 5. Si hi ha línies lliures, afegir títol + seleccionables de la
        #    secció següent, però mai acabar amb un títol sol
        remaining = MgrOptsel.LINES_PER_PAGE - len(display)
        if remaining > 0:
            next_title = None
            next_title_idx = None
            for i, it in enumerate(options):
                if it.get('code') is None and it is not active_title:
                    if active_title_idx is None or i > active_title_idx:
                        next_title = it
                        next_title_idx = i
                        break
            if next_title is not None and remaining >= 2:
                # caben títol + almenys 1 seleccionable
                next_items = []
                for it in options[next_title_idx + 1:]:
                    if it.get('code') is None:
                        break
                    next_items.append(it)
                display.append(next_title)
                display += next_items[:remaining - 1]

        display = display[:MgrOptsel.LINES_PER_PAGE]

        lines_html = [
            self._render_item_html(it,
                is_highlighted=(it.get('code') == cursor),
                show_code=show_code,
                ts=ts,
                is_title=(it.get('code') is None))
            for it in display
        ]

        html = self._build_screen_html(lines_html, ts)
        self.mgr_guispy.write_screen_html(html)

    def _show_filtered_list(self, filter_digits):
        """Mostra la llista filtrada (sense títols, llista plana)."""
        session   = self._session
        cursor    = session.get('cursor_code')
        show_code = session['show_code']
        ts = session['ts']

        filtered  = self._visible_selectable_items()
        sel_codes = [it['code'] for it in filtered]
        cursor_idx = sel_codes.index(cursor) if cursor in sel_codes else 0
        page, _   = divmod(cursor_idx, MgrOptsel.LINES_PER_PAGE)
        page_items = filtered[page * MgrOptsel.LINES_PER_PAGE:
                               (page + 1) * MgrOptsel.LINES_PER_PAGE]

        lines_html = [
            self._render_item_html(it, is_highlighted=(it['code'] == cursor),
                                   show_code=show_code, ts=ts, is_title=False)
            for it in page_items
        ]
        html = self._build_screen_html(lines_html, ts)
        self.mgr_guispy.write_screen_html(html)

    def _render_item_html(self, item, is_highlighted, show_code, ts, is_title):
        """Genera el fragment HTML per a un element de la llista."""
        label = item.get('label', '')
        code  = item.get('code')
        color = item.get('color')
        background_color = item.get('background_color')
        style = item.get('style', [])

        # text a mostrar
        if is_title:
            text = label
        elif show_code and code:
            text = f'{code} - {label}'
        else:
            text = label

        # color de text: el del tema per defecte, sobreescrit per color de l'element
        fg_color = ts['hl_fg'] if is_highlighted else color if color else ts['fg']
        bg_color = ts['hl_bg'] if is_highlighted else background_color if background_color else 'transparent'

        # estils tipogràfics
        font_weight  = 'bold'   if 'bold'      in style else 'normal'
        text_decoration = 'underline' if 'underline' in style else 'none'

        css = (f'font-weight:{font_weight};'
               f'text-decoration:{text_decoration};'
               f'color:{fg_color};'
               f'background-color:{bg_color};'
               f'margin:11px 0 0 0;padding:0 0 0 10px;white-space:nowrap;overflow:hidden;')

        return f'<h2 style="{css}">{text}</h2>'

    def _build_screen_html(self, lines_html, ts):
        container_style = (
            f'width:320px;height:240px;'
            f'background-color:{ts["bg"]};'
            f'color:{ts["fg"]};'
            f'text-align:left;'
            f'overflow:hidden;'
        )
        inner = ''.join(lines_html)
        return f'<div style="{container_style}">{inner}</div>'

    # ── timer ──────────────────────────────────────────────────────────────────

    def _reset_timer(self):
        session = self._session
        if session is not None:
            timeout = session.get('keyboard_timeout', MgrOptsel.KEYBOARD_TIMEOUT_DEFAULT)
            self.keyboard_timer.set_tmo(timeout)

    # ── buzzer ─────────────────────────────────────────────────────────────────

    def _beep(self, style):
        """Crida el buzzer."""
        try:
            self.buzzer_fp(style)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)}')

    # ── decode tecla ───────────────────────────────────────────────────────────

    @staticmethod
    def _decode_key(s_key):
        mapping = {
            'A': 'OK',
            'B': 'MENU',   # serigrafiat com a menu/paginació; antiga tecla BACK
            'C': 'UP',
            'D': 'DOWN',
        }
        if s_key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return s_key
        return mapping.get(s_key)

    # ── parse i validació ──────────────────────────────────────────────────────

    def _parse_and_validate(self, msg_arg):
        """
        Valida tots els arguments de ins_optsel_run.
        Llença excepció si alguna validació falla (→ RET_INVALIDARGUMENT al caller).
        Retorna un dict de sessió ja validat i llest per usar.
        """
        # ── options ──
        options_raw = msg_arg.get('options')
        if not isinstance(options_raw, list):
            raise ValueError('options must be a list')

        options = self._parse_options(options_raw)

        button_b_action = KCheck.elementInList(
            msg_arg.get('button_b_action', MgrOptsel.BUTTON_B_ACTION_DEFAULT),
            MgrOptsel.BUTTON_B_ACTION_LIST
        )

        # ── keyboard_timeout ──
        keyboard_timeout = KCheck.integerInInterval(
            msg_arg.get('keyboard_timeout', MgrOptsel.KEYBOARD_TIMEOUT_DEFAULT),
            MgrOptsel.KEYBOARD_TIMEOUT_MIN,
            MgrOptsel.KEYBOARD_TIMEOUT_MAX,
        )

        # ── show_code ──
        show_code = KCheck.booleanValue(msg_arg.get('show_code', True))

        # ── theme ──
        theme = KCheck.elementInList(
            msg_arg.get('theme', MgrOptsel.THEME_DEFAULT),
            MgrOptsel.THEME_LIST,
        )
        theme_style_bg = msg_arg.get('theme_style_bg')
        theme_style_fg = msg_arg.get('theme_style_fg')
        theme_style_hl_bg = msg_arg.get('theme_style_hl_bg')
        theme_style_hl_fg = msg_arg.get('theme_style_hl_fg')
        ts = dict(MgrOptsel.THEME_STYLES[theme])
        if theme_style_bg:
            ts['bg'] = theme_style_bg
        if theme_style_fg:
            ts['fg'] = theme_style_fg
        if theme_style_hl_bg:
            ts['hl_bg'] = theme_style_hl_bg
        if theme_style_hl_fg:
            ts['hl_fg'] = theme_style_hl_fg

        # ── key_beep ──
        key_beep = KCheck.booleanValue(msg_arg.get('key_beep', True))

        # ── default_code ──
        default_code = msg_arg.get('default_code')
        if default_code is not None:
            sel_codes = [it['code'] for it in options if it.get('code') is not None]
            if default_code not in sel_codes:
                raise ValueError('default_code not found among selectable options')

        # ── msg_id (opac, opcional) ──
        msg_id = msg_arg.get('msgId', msg_arg.get('msg_id'))  # acceptem les dues grafies

        return {
            'options':          options,
            'button_b_action': button_b_action,
            'keyboard_timeout': keyboard_timeout,
            'show_code':        show_code,
            'ts': ts,
            'key_beep':         key_beep,
            'default_code':     default_code,
            'msg_id':           msg_id,
        }

    def _parse_options(self, options_raw):
        """
        Valida i normalitza la llista d'opcions.
        Regles:
          - 1..100 elements
          - si hi ha títols (code absent/null), el primer element ha de ser títol
          - cada títol ha de tenir almenys un element seleccionable a continuació
            (no es permeten seccions buides)
          - code únic entre seleccionables
          - code: string numèric, 1-8 caràcters
          - label: string, 1-25 caràcters
          - ref: string, 1-64 caràcters (només en seleccionables)
          - style: llista de valors vàlids
        """
        if not (MgrOptsel.OPTIONS_MIN <= len(options_raw) <= MgrOptsel.OPTIONS_MAX):
            raise ValueError(f'options length must be between '
                             f'{MgrOptsel.OPTIONS_MIN} and {MgrOptsel.OPTIONS_MAX}')

        options = []
        seen_codes = set()
        has_titles = False
        selectable_count = 0
        last_title_idx = None   # índex a options[] de l'últim títol sense seleccionable encara

        for i, raw in enumerate(options_raw):
            if not isinstance(raw, dict):
                raise ValueError(f'options[{i}] must be a dict')

            code  = raw.get('code')
            label = raw.get('label')
            ref   = raw.get('ref')
            color = raw.get('color')        # opac per a la validació; el renderer el gestiona
            background_color = raw.get('background_color')
            style = raw.get('style', [])

            # label obligatori sempre
            label = KCheck.stringLenInInterval(label,
                                               MgrOptsel.LABEL_LEN_MIN,
                                               MgrOptsel.LABEL_LEN_MAX)

            # style
            if not isinstance(style, list):
                raise ValueError(f'options[{i}].style must be a list')
            for sv in style:
                if sv not in MgrOptsel.STYLE_VALID:
                    raise ValueError(f'options[{i}].style invalid value: {sv}')

            if code is None:
                # títol de secció
                # si ja hi havia un títol pendent sense seleccionables → secció buida
                if last_title_idx is not None:
                    raise ValueError(f'options[{last_title_idx}]: section title has no '
                                     f'selectable elements before next title at [{i}]')
                has_titles = True
                last_title_idx = len(options)   # posició del títol a la llista en construcció
                # ref ha de ser absent en títols
                if ref is not None:
                    raise ValueError(f'options[{i}]: ref must be absent in section titles')
                item = {'label': label}
                if color is not None:
                    item['color'] = color
                if background_color is not None:
                    item['background_color'] = background_color
                if style:
                    item['style'] = style
            else:
                # element seleccionable: consumeix el títol pendent
                last_title_idx = None
                # code: string numèric 1-8
                if not isinstance(code, str):
                    raise ValueError(f'options[{i}].code must be a string')
                if not (MgrOptsel.CODE_LEN_MIN <= len(code) <= MgrOptsel.CODE_LEN_MAX):
                    raise ValueError(f'options[{i}].code length out of range')
                if not code.isdigit():
                    raise ValueError(f'options[{i}].code must contain only digits')
                if code in seen_codes:
                    raise ValueError(f'options[{i}].code is not unique: {code}')
                seen_codes.add(code)
                selectable_count += 1

                item = {'code': code, 'label': label}
                if ref is not None:
                    ref = KCheck.stringLenInInterval(ref,
                                                     MgrOptsel.REF_LEN_MIN,
                                                     MgrOptsel.REF_LEN_MAX)
                    item['ref'] = ref
                if color is not None:
                    item['color'] = color
                if background_color is not None:
                    item['background_color'] = background_color
                if style:
                    item['style'] = style

            options.append(item)

        # títol al final de la llista sense seleccionables
        if last_title_idx is not None:
            raise ValueError(f'options[{last_title_idx}]: section title has no '
                             f'selectable elements')

        # si hi ha títols, el primer element ha de ser títol
        if has_titles and options[0].get('code') is not None:
            raise ValueError('if titles are present, first element must be a title')

        # almenys un seleccionable
        if selectable_count == 0:
            raise ValueError('options must contain at least one selectable element')

        return options