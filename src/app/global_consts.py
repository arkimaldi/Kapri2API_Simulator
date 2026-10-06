# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.


class GlobalConsts:
    gc_dict = {

        # --- nano_configuration
        # values
        'const_network_dhcp_mode_values': ['DHCP', 'Manual'],
        'const_ktp_server_client_mode_values': ['Server', 'Client'],
        'const_jso_server_client_mode_values': ['Server', 'Client'],
        'const_scankey_encoding_values': ['R4x1', 'D4x1', 'R4x4', 'D4x4'],
        # sizes
        'const_terminal_description_lenmin': 1,
        'const_terminal_description_size': 255,
        'const_wlan_ssid_lenmin': 1,
        'const_wlan_ssid_size': 32,
        'const_wlan_password_lenmin': 8,
        'const_wlan_password_size': 63,
        'const_interface_ins_pwd_lenmin': 0,
        'const_interface_ins_pwd_size': 500,
        'const_ktp_network_id_lenmin': 10,
        'const_ktp_network_id_size': 40,
        'const_ktp_aes256_size': 64,
        'const_cloud_remote_server_url_lenmin': 0,
        'const_cloud_remote_server_url_size': 500,
        'const_cloud_remote_server_token_lenmin': 0,
        'const_cloud_remote_server_token_size': 500,
        'const_cloud_allowed_events_lenmin': 0,
        'const_semi_offline_batch_lenmin': 0,
        'const_cloud_allowed_events_size': 500,
        'const_semi_offline_batch_size': 2048,
        'const_scankey_encoding_size': 10,
        'const_kybmgr_cfg_1_lenmin': 0,
        'const_kybmgr_cfg_1_size': 2048,
        'const_screen_html_boot_lenmin': 0,
        'const_screen_html_boot_size': 2048,

        # --- semi_offline_events
        # sizes
        'const_semi_offline_event_json_lenmin': 0,
        'const_semi_offline_event_json_size': 2048,
        # count
        'const_max_num_semi_offline_events_in_table': 10000,
        'const_num_semi_offline_events_to_delete': 1000,

        # --- semi_offline_lists
        'const_semi_offline_list_blob_lenmin': 0,
        'const_semi_offline_list_blob_lenmax': 4*1024*1024,
        'const_semi_offline_list_blob_size': (2 ** 24) - 1,

        # --- images
        'const_images_max_file_size': 225 * 1024,
        'const_images_max_number_of_files_in_directory': 1000,
        'const_images_included_extensions': ['.jpg', '.jpeg', '.bmp', '.png', '.gif'],
        'const_images_excluded_names_to_store': ['demo_landscape.jpg', 'demo_background.jpg', 'kapri_boot.jpg', 'kapri_post_loading.png', 'kapri_test.jpg'],
        'const_images_excluded_names_to_remove': ['demo_landscape.jpg', 'demo_background.jpg', 'kapri_boot.jpg', 'boot.jpg', 'kapri_post_loading.png', 'post_loading.png', 'kapri_test.jpg'],

        # --- knet_id
        'const_knet_id_lexa': 174,
        'const_knet_id_kapri': 176,

        # --- identification
        'const_my_uc_model_no': 176, # Online 176, offline 180
        'const_my_sname': 'Kapri Online', # Online 'Kapri Online', ofline 'Kapri Offline'
        'const_my_version': '2.0.7',

    }

    @staticmethod
    def set(key, value):
        if key not in GlobalConsts.gc_dict.keys():
            raise
        GlobalConsts.gc_dict[key] = value

    @staticmethod
    def get(key):
        return GlobalConsts.gc_dict[key]

