# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import threading
import queue
import inspect
import logging
import textwrap
from collections import defaultdict

from app.MgrKybmgr.k_timer import KTimer
from app.MgrKybmgr.k_check import KCheck


class MgrKybmgr:

    QUEUE_BRET_TIMEOUT = 5
    DO_PAUSE_TIMEOUT = 30
    I_KEYBOARD_TIMEOUT_DEFAULT = 5
    I_KEYBOARD_TIMEOUT_MIN = 1
    I_KEYBOARD_TIMEOUT_OPERATIVE_MIN = 3
    I_KEYBOARD_TIMEOUT_MAX = 10
    I_PROMPT_TIMEOUT_DEFAULT = 10
    I_PROMPT_TIMEOUT_MIN = 5
    I_PROMPT_TIMEOUT_MAX = 60
    S_HTML_BLANK = '<h1></h1>'
    S_HTML_INPUT_DEFAULT = ''
    S_HTML_OUTPUT_DEFAULT = '<h2>#KYBMGR_CODE? - #KYBMGR_DESCRIPTION?</h2>'
    S_HTML_PROMPT_DEFAULT = '<h2> Enter Code: ________ </h2>'
    CODE_SELECTION_LIST = ['prompt', 'first', 'last_choice']
    CODE_SELECTION_DEFAULT = CODE_SELECTION_LIST[2]
    MENU_LINES_PER_PAGE = 4

    def __init__(self, app, mgr_guispy):
        try:
            self.app = app
            self.mgr_guispy = mgr_guispy
            # objectes
            self.incoming_events_queue = queue.Queue()
            self.configure_bret_queue = queue.Queue()
            self.pause_bret_queue = queue.Queue()
            self.resume_bret_queue = queue.Queue()
            self.keyboard_timer = KTimer(self.on_keyboard_timer)
            self.prompt_timer = KTimer(self.on_prompt_timer)
            # iniciem objectes
            self.keyboard_timer.clear_tmo()
            self.prompt_timer.clear_tmo()
            self.incoming_events_queue.queue.clear()
            self.configure_bret_queue.queue.clear()
            self.pause_bret_queue.queue.clear()
            self.resume_bret_queue.queue.clear()
            # iniciem propietats...
            # ... de configuració
            self.s_html_input = None
            self.s_html_output = None
            self.s_html_prompt = None
            self.code_selection = None
            self.codes_list = None
            self.menu_codes_list = None
            self.code_description_dict = None
            self.shortcut_codes_dict = None
            self.shortcut_reverse_dict = None
            self.i_keyboard_timeout = None
            self.i_prompt_timeout = None
            # ... d'estat
            self.current_parsed_configuration = None  # None indica que el mòdul no opera.
            self.b_scratch = True  # True: indica que no s'ha establert cap configuració des de la instanciació
            self.paused = None
            self.code = None
            self.s_keyboard_input = None
            self.machine_screen = None
            # fil
            self.main_thread = None
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def start(self):
        self.main_thread = threading.Thread(target=self.main_thread_task, daemon=True)
        self.main_thread.start()

    def get_code_and_description(self):
        kybmgr_dict = None
        if self.code is not None:
            description = ''
            try:
                description = self.code_description_dict[self.code]
            except:
                description = ''
            finally:
                kybmgr_dict = {'code': self.code, 'description': description}
        return kybmgr_dict

    def on_key_received(self, s_key):
        self.on_incoming_event({'msgType': 'on_keyboard_echo', 'msgArg': {'sKey': s_key}})

    def configure(self, desired_configuration):
        b_ret = False
        try:
            self.on_incoming_event({'msgType': 'on_kybmgr_configuration', 'msgArg': {'desired_configuration': desired_configuration}})
            # esperem que la màquina d'events ens retorni b_ret
            b_ret = self.configure_bret_queue.get(block=True, timeout=MgrKybmgr.QUEUE_BRET_TIMEOUT)
        except:
            b_ret = False
        finally:
            return b_ret

    def pause(self):
        try:
            self.on_incoming_event({'msgType': 'on_kybmgr_pause', 'msgArg': {}})
            # esperem que la màquina d'events acabi
            self.pause_bret_queue.get(block=True, timeout=MgrKybmgr.QUEUE_BRET_TIMEOUT)
        except:
            pass

    def resume(self):
        try:
            self.on_incoming_event({'msgType': 'on_kybmgr_resume', 'msgArg': {}})
            # esperem que la màquina d'events acabi
            self.resume_bret_queue.get(block=True, timeout=MgrKybmgr.QUEUE_BRET_TIMEOUT)
        except:
            pass

    #  ---- privat
    def on_keyboard_timer(self):
        self.on_incoming_event({'msgType': 'on_keyboard_timeout', 'msgArg': {}})

    def on_prompt_timer(self):
        self.on_incoming_event({'msgType': 'on_prompt_timeout', 'msgArg': {}})

    def on_incoming_event(self, incoming_event):
        try:
            self.incoming_events_queue.put(incoming_event)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def main_thread_task(self):
        while True:
            try:
                event = self.incoming_events_queue.get()
                self.state_machine(event)
            except Exception as e:
                logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def state_machine(self, event_in):
        try:
            msg_type = event_in['msgType']
            msg_arg = event_in['msgArg']

            # instruccions externes
            if msg_type == 'on_kybmgr_configuration':
                self.do_configuration(msg_arg['desired_configuration'], bret_queue=True)
            elif msg_type == 'on_kybmgr_pause':
                self.do_pause(bret_queue=True)
            elif msg_type == 'on_kybmgr_resume':
                self.do_resume(bret_queue=True)
            else:
                # operativa interna
                if self.current_parsed_configuration is not None:
                    if self.paused:
                        if msg_type == 'on_keyboard_timeout':
                            self.do_resume(bret_queue=False)
                    else:  # not paused
                        if msg_type == 'on_keyboard_timeout':
                            if self.machine_screen in ['input', 'menu']:
                                # simulem la pulsació d'OK per sortir de la pantalla input
                                self.on_incoming_event({'msgType': 'on_keyboard_echo', 'msgArg': {'sKey': 'A'}})
                        elif msg_type == 'on_prompt_timeout':  # només pot existir en ['output', 'input', 'menu']:
                            self.code = None
                            self.machine_screen = 'prompt'
                            self.show_screen()
                        elif msg_type == 'on_keyboard_echo':
                            s_key_name = self.decode_key(msg_arg['sKey'])
                            if s_key_name == 'BACK':
                                if self.machine_screen in ['prompt', 'output']:
                                    self.init_menu_screen()
                                    self.machine_screen = 'menu'
                                elif self.machine_screen == 'input':
                                    if self.current_parsed_configuration['code_selection'] == 'prompt':
                                        self.code = None
                                    self.goto_output_or_prompt()
                                elif self.machine_screen == 'menu':
                                    self.menu_roll_forwards()
                                self.show_screen()
                            elif s_key_name == 'UP':
                                if self.machine_screen in ['prompt', 'output']:
                                    self.machine_screen = 'output'
                                    self.look_backwards()
                                elif self.machine_screen == 'input':
                                    pass  # sense efecte
                                elif self.machine_screen == 'menu':
                                    self.menu_look_backwards()  # mantenim pantalla menu
                                self.show_screen()
                            elif s_key_name == 'DOWN':
                                if self.machine_screen in ['prompt', 'output']:
                                    self.machine_screen = 'output'
                                    self.look_forwards()
                                elif self.machine_screen == 'input':
                                    pass  # sense efecte
                                elif self.machine_screen == 'menu':
                                    self.menu_look_forwards()  # mantenim pantalla menu
                                self.show_screen()
                            elif s_key_name == 'OK':
                                if self.machine_screen == 'input':
                                    if self.s_keyboard_input is not None:
                                        self.set_code_if_is_valid(int(self.s_keyboard_input))
                                    self.goto_output_or_prompt()
                                elif self.machine_screen == 'menu':
                                    self.machine_screen = 'output'
                                self.show_screen()
                            elif s_key_name in ['F1', 'F2']:
                                if self.machine_screen in ['prompt', 'output', 'input', 'menu']:
                                    self.set_code_if_is_valid(self.shortcut_codes_dict.get(s_key_name))
                                    self.goto_output_or_prompt()
                                self.show_screen()
                            elif s_key_name in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                                if self.machine_screen in ['prompt', 'output']:
                                    self.s_keyboard_input = None
                                self.append_to_keyboard_input(s_key_name)

                                # pas ràpid a screens input o menu incorporant s_digit
                                if self.machine_screen in ['prompt', 'output']:
                                    if self.s_html_input:
                                        self.machine_screen = 'input'
                                    else:
                                        self.init_menu_screen(init_keyboard_input=False)
                                        self.machine_screen = 'menu'

                                # tractem pantalles
                                if self.machine_screen == 'input':
                                    if not self.keyboard_input_can_be_tens():
                                        if self.set_code_if_is_valid(int(self.s_keyboard_input)):
                                            self.goto_output_or_prompt()
                                        else:
                                            self.s_keyboard_input = self.s_keyboard_input[:-1]
                                elif self.machine_screen == 'menu':
                                    if not self.keyboard_input_can_be_tens():
                                        if self.set_code_if_is_valid(int(self.s_keyboard_input)):
                                            self.goto_output_or_prompt()
                                        else:
                                            self.s_keyboard_input = self.s_keyboard_input[:-1]
                                    else:
                                        self.filter_menu_by_start_digits(
                                            self.s_keyboard_input)  # mantenim pantalla menu
                                        self.set_code_if_is_valid(int(self.s_keyboard_input))
                                self.show_screen()

                            if self.current_parsed_configuration['code_selection'] == 'prompt':
                                if self.machine_screen in ['output', 'input', 'menu']:
                                    self.prompt_timer.set_tmo(self.i_prompt_timeout)
                            if self.machine_screen in ['input', 'menu']:
                                self.keyboard_timer.set_tmo(self.i_keyboard_timeout)

        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def autocall(self):
        event = {'msgType': 'autocall', 'msgArg': {}}
        self.incoming_events_queue.put(event)

    def load_configuration(self, desired_configuration, bret_queue=False):
        try:
            parsed_configuration = self.check_and_parse_desired_configuration(desired_configuration)
            self.apply_parsed_configuration(parsed_configuration)
            self.current_parsed_configuration = parsed_configuration
            self.mgr_guispy.set_guispy_sequence_mode('extended')
            self.b_scratch = False
        except:
            self.current_parsed_configuration = None
            self.paused = None
            self.code = None
            self.s_keyboard_input = None
            self.machine_screen = None
            self.mgr_guispy.set_guispy_sequence_mode('standard')
        finally:
            if bret_queue:
                b_ret = self.current_parsed_configuration is not None
                self.configure_bret_queue.put(b_ret)  # informem a configure

    def check_and_parse_desired_configuration(self, desired_configuration):
        s_html_input = KCheck.stringLenInInterval(desired_configuration.get('s_html_input', MgrKybmgr.S_HTML_INPUT_DEFAULT), 0, 9999)
        s_html_output = KCheck.stringLenInInterval(desired_configuration.get('s_html_output', MgrKybmgr.S_HTML_OUTPUT_DEFAULT), 1, 9999)
        s_html_prompt = KCheck.stringLenInInterval(desired_configuration.get('s_html_prompt', MgrKybmgr.S_HTML_PROMPT_DEFAULT), 1, 9999)
        code_selection = KCheck.elementInList(desired_configuration.get('code_selection', MgrKybmgr.CODE_SELECTION_DEFAULT), MgrKybmgr.CODE_SELECTION_LIST)
        codes_list, code_description_dict = self.ckeck_and_parse_allowed_codes_list(desired_configuration['allowed_codes_list'])
        shortcut_codes_dict = self.check_shortcut_codes_dict(desired_configuration.get('shortcut_codes_dict', {}))
        i_keyboard_timeout = KCheck.integerInInterval(
            desired_configuration.get('keyboard_timeout', MgrKybmgr.I_KEYBOARD_TIMEOUT_DEFAULT),
            MgrKybmgr.I_KEYBOARD_TIMEOUT_MIN,
            MgrKybmgr.I_KEYBOARD_TIMEOUT_MAX
        )
        if i_keyboard_timeout < MgrKybmgr.I_KEYBOARD_TIMEOUT_OPERATIVE_MIN:
            i_keyboard_timeout = MgrKybmgr.I_KEYBOARD_TIMEOUT_OPERATIVE_MIN
        i_prompt_timeout = KCheck.integerInInterval(
            desired_configuration.get('prompt_timeout', MgrKybmgr.I_PROMPT_TIMEOUT_DEFAULT),
            MgrKybmgr.I_PROMPT_TIMEOUT_MIN,
            MgrKybmgr.I_PROMPT_TIMEOUT_MAX
        )
        parsed_configuration = {
            's_html_input': s_html_input,
            's_html_output': s_html_output,
            's_html_prompt': s_html_prompt,
            'code_selection': code_selection,
            'codes_list': codes_list,
            'code_description_dict': code_description_dict,
            'shortcut_codes_dict': shortcut_codes_dict,
            'i_keyboard_timeout': i_keyboard_timeout,
            'i_prompt_timeout': i_prompt_timeout
        }
        return parsed_configuration

    def ckeck_and_parse_allowed_codes_list(self, allowed_codes_list):
        if not isinstance(allowed_codes_list, list):
            raise
        if not allowed_codes_list:
            raise
        codes_list = []
        code_description_dict = {}
        for x in allowed_codes_list:
            if not isinstance(x, list):
                raise
            i_code = KCheck.integerInInterval(x[0], 0, 99999999)
            s_description = KCheck.stringLenInInterval(x[1], 1, 25)
            codes_list.append(i_code)
            code_description_dict[i_code] = s_description
        return codes_list, code_description_dict

    def check_shortcut_codes_dict(self, shortcut_codes_dict):
        if not isinstance(shortcut_codes_dict, dict):
            raise
        KCheck.integerInInterval(shortcut_codes_dict.get('F1', 0), 0, 99999999)
        KCheck.integerInInterval(shortcut_codes_dict.get('F2', 0), 0, 99999999)
        return shortcut_codes_dict

    def build_shortcut_reverse_dict(self, shortcut_codes_dict):
        grouped = defaultdict(list)
        for key, value in shortcut_codes_dict.items():
            grouped[str(value)].append(key)  # str(value) = new key
        shortcut_reverse_dict = {k: "/".join(keys) for k, keys in grouped.items()}
        return shortcut_reverse_dict

    def apply_parsed_configuration(self, parsed_configuration):
        # -- configuració
        self.s_html_input = parsed_configuration['s_html_input']
        self.s_html_output = parsed_configuration['s_html_output']
        self.s_html_prompt = parsed_configuration['s_html_prompt']
        self.code_selection = parsed_configuration['code_selection']
        self.codes_list = parsed_configuration['codes_list']
        self.code_description_dict = parsed_configuration['code_description_dict']
        self.shortcut_codes_dict = parsed_configuration['shortcut_codes_dict']
        self.shortcut_reverse_dict = self.build_shortcut_reverse_dict(self.shortcut_codes_dict)
        self.i_keyboard_timeout = parsed_configuration['i_keyboard_timeout']
        self.i_prompt_timeout = parsed_configuration['i_prompt_timeout']
        # -- estat
        self.paused = False
        self.s_keyboard_input = None
        # self.code
        if self.code_selection == 'prompt':
            new_code = None
        elif self.code_selection == 'first':
            new_code = self.codes_list[0]
        else:  # 'last_choice'
            if self.code in self.codes_list:
                new_code = self.code
            else:
                new_code = self.codes_list[0]
        self.code = new_code
        # machine screen
        if self.code_selection == 'prompt':
            self.machine_screen = 'prompt'
        else:  # 'first' o 'last_choice'
            self.machine_screen = 'output'

    def do_configuration(self, desired_configuration, bret_queue=False):
        self.load_configuration(desired_configuration, bret_queue)
        self.show_screen()

    def do_pause(self, bret_queue=False):
        try:
            if self.current_parsed_configuration is not None:
                if not self.paused:
                    self.paused = True
                    self.keyboard_timer.set_tmo(MgrKybmgr.DO_PAUSE_TIMEOUT)
        except:
            pass
        finally:
            if bret_queue:
                self.pause_bret_queue.put('done')  # informem a pause

    def do_resume(self, bret_queue=False):
        try:
            if self.current_parsed_configuration is not None:
                if self.paused:
                    self.keyboard_timer.clear_tmo()
                    self.apply_parsed_configuration(self.current_parsed_configuration)
                    self.show_screen()
        except:
            pass
        finally:
            if bret_queue:
                self.resume_bret_queue.put('done')  # informem a resume

    def set_code_if_is_valid(self, i_code):
        if i_code in self.codes_list:
            self.code = i_code
            return True
        return False

    def decode_key(self, sKey):
        if sKey in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return sKey
        elif sKey == 'A':
            return 'OK'
        elif sKey == 'B':
            return 'BACK'
        elif sKey == 'C':
            return 'UP'
        elif sKey == 'D':
            return 'DOWN'
        elif sKey == 'E':
            return 'F1'
        elif sKey == 'F':
            return 'F2'
        else:
            return None

    def append_to_keyboard_input(self, s_dig):
        if self.s_keyboard_input is None:
            self.s_keyboard_input = s_dig
        else:
            self.s_keyboard_input = self.s_keyboard_input + s_dig

    def keyboard_input_can_be_tens(self):
        for code in self.codes_list:
            s_code = f'{code}'
            if s_code[0:len(self.s_keyboard_input)] == self.s_keyboard_input:
                if len(s_code) > len(self.s_keyboard_input):
                    return True
        return False

    def look_forwards(self):
        if self.code is None:
            self.code = self.codes_list[0]
        else:
            curr_pos = self.codes_list.index(self.code)
            if curr_pos + 1 < len(self.codes_list):
                curr_pos += 1
            self.code = self.codes_list[curr_pos]

    def look_backwards(self):
        if self.code is None:
            self.code = self.codes_list[0]
        else:
            curr_pos = self.codes_list.index(self.code)
            if curr_pos > 0:
                curr_pos -= 1
            self.code = self.codes_list[curr_pos]

    def init_menu_screen(self, init_keyboard_input=True):
        self.menu_codes_list = list(self.codes_list)
        if self.code is None:
            self.code = self.menu_codes_list[0]
        if init_keyboard_input:
            self.s_keyboard_input = None

    def menu_look_backwards(self):
        if self.code is None:
            self.code = self.menu_codes_list[0]
        else:
            curr_pos = self.menu_codes_list.index(self.code)
            if curr_pos > 0:
                curr_pos -= 1
            self.code = self.menu_codes_list[curr_pos]

    def menu_look_forwards(self):
        if self.code is None:
            self.code = self.menu_codes_list[0]
        else:
            curr_pos = self.menu_codes_list.index(self.code)
            if curr_pos + 1 < len(self.menu_codes_list):
                curr_pos += 1
            self.code = self.menu_codes_list[curr_pos]

    def menu_roll_forwards(self):
        if self.code is None:
            self.code = self.menu_codes_list[0]
        else:
            curr_pos = self.menu_codes_list.index(self.code)
            page, line = divmod(curr_pos, MgrKybmgr.MENU_LINES_PER_PAGE)
            curr_pos = (page + 1) * MgrKybmgr.MENU_LINES_PER_PAGE
            if curr_pos >= len(self.menu_codes_list):
                curr_pos = 0
            self.code = self.menu_codes_list[curr_pos]

    def filter_menu_by_start_digits(self, s_start_digits):
        """
        Determines whether self.codes_list contains integers
        whose decimal string representation starts with s_start_digit.
        Being s_start_digit: a string with one or more digits, e.g. '2' or '21'

        In that case only, replaces self.menu_codes_list with those integers
        that meet the condition. If the current self.code is not in the newly filtered self.menu_codes_list,
        self.code is replaced with the first code in the filtered result.

        """
        filtered_codes_list = [code for code in self.codes_list if str(code).startswith(s_start_digits)]
        if filtered_codes_list:
            self.menu_codes_list = filtered_codes_list
            if self.code not in self.menu_codes_list:
                self.code = self.menu_codes_list[0]

    def goto_output_or_prompt(self):
        if self.current_parsed_configuration['code_selection'] == 'prompt':
            if self.code is None:
                self.machine_screen = 'prompt'
            else:
                self.machine_screen = 'output'
        else:
            self.machine_screen = 'output'

    def show_screen_blank(self):
        try:
            html_to_send = MgrKybmgr.S_HTML_BLANK
            self.mgr_guispy.write_screen_html(html_to_send)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def show_screen_for_input(self):
        try:
            s_input = f'{self.s_keyboard_input}_'
            html_to_send = self.s_html_input
            html_to_send = html_to_send.replace('#KYBMGR_INPUT?', s_input)
            self.mgr_guispy.write_screen_html(html_to_send)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def show_screen_for_output(self):
        try:
            s_code = f'{self.code}'
            s_description = self.code_description_dict[self.code]
            html_to_send = self.s_html_output
            html_to_send = html_to_send.replace('#KYBMGR_CODE?', s_code)
            html_to_send = html_to_send.replace('#KYBMGR_DESCRIPTION?', s_description)
            self.mgr_guispy.write_screen_html(html_to_send)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def show_screen_for_prompt(self):
        try:
            html_to_send = self.s_html_prompt
            self.mgr_guispy.write_screen_html(html_to_send)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def show_screen_for_menu(self):
        try:
            curr_pos = self.menu_codes_list.index(self.code)
            page, line = divmod(curr_pos, MgrKybmgr.MENU_LINES_PER_PAGE)
            init_pos = page * MgrKybmgr.MENU_LINES_PER_PAGE
            screen_codes_list = self.menu_codes_list[init_pos: init_pos + MgrKybmgr.MENU_LINES_PER_PAGE]

            html_to_send = textwrap.dedent('''
                <style>
                  .line {
                    font-weight: normal;
                    margin: 25px 0 0 0;
                    padding: 0 0 0 10px;
                  }

                  .line--highlight {
                    background-color: white;
                    color: black;
                  }
                </style>
            ''')
            html_to_send += '<div style="width:320px;height:240px;color:white;background-color:#16252c;text-align:left;white-space: nowrap;overflow: hidden;">'
            for code in screen_codes_list:
                s_code = f'{code}'
                s_description = self.code_description_dict[code]
                css_class = 'line line--highlight' if code == self.code else 'line'
                html_to_send += f'<h2 class="{css_class}">{s_code} - {s_description}</h2>'
            html_to_send += '</div>'
            self.mgr_guispy.write_screen_html(html_to_send)
        except Exception as e:
            logging.error(f'{inspect.stack()[0][3]} Exception: {str(e)} (called by: {inspect.stack()[1][3]})')

    def get_current_screen(self):
        """
        Aquest procediment calcula la pantalla a mostrar a partir de la interpretació de les variables d'estat:
            self.current_parsed_configuration
            self.b_scratch
            self.paused
            self.machine_screen
        """
        current_screen = None
        if self.current_parsed_configuration is None:
            if not self.b_scratch:
                current_screen = 'blank'
        else:
            if not self.paused:
                current_screen = self.machine_screen
        return current_screen

    def show_screen(self):
        current_screen = self.get_current_screen()
        if current_screen == 'blank':
            self.show_screen_blank()
        elif current_screen == 'prompt':
            self.show_screen_for_prompt()
        elif current_screen == 'output':
            self.show_screen_for_output()
        elif current_screen == 'input':
            self.show_screen_for_input()
        elif current_screen == 'menu':
            self.show_screen_for_menu()

