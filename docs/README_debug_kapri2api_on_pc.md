# Debugging Kapri Online

Kapri2Online is a product composed of several microservices that run on an embedded Linux platform. 
In this document, we will explain the steps necessary to configure the system to allow the Kapri2API microservice to run 
on a PC and be debugged in a step-by-step manner.

## Prerequisites

Before proceeding with the debugging process, ensure that the following prerequisites are met:

- MariaDB and Heidi are installed on your PC.
- PyCharm is installed on the PC
- The Kapri2API project is cloned on your PC
- Python 3.8 venv is set as interpreter
- And all necessary dependencies are correctly installed in the virtual environment (venv).

## Configuring the System

To configure the system for debugging Kapri2API, follow these steps:

1. Open the Kapri2API project in PyCharm:
   1. Create an interpreter based on Python 3.8
   2. Add the `/source` directory to the interpreter path
   3. Install all dependencies in the venv for Windows using `pip install -r requirements.txt`.
   4. Run Kapri2API file and edit the working directory to remove `/src`.
   5. Copy `Kapri2API.conf` as `Kapri2API_default.conf`.
2. Modify the configuration file (Kapri2API_default.conf) of the Kapri2API microservice:
   1. `api_host = "127.0.0.1"` to `api_host = "0.0.0.0"`
   2. `debug_level = "ERROR"` to `debug_level = "DEBUG"`
   3. Replace all references to the address 127.0.0.1 with the IP address of the embedded Linux platform (e.g., 10.0.0.76). 
   These references are in `[url]` and `[socketio]` segments.
   4. All these steps will bring the configuration file to the state saved in `Kapri2API_sample_debug_on_pc.conf`
3. Create a directory named `imgrepo` in the project root directory and  set the [routes] segment of the configuration file
to `routes_imgrepo_dir = 'imgrepo/'`. This is only to allow the service to run. Image managing will not work properly since other 
micro-services may be accessing the directory present in the embedded.
4. Add the directory `license` and create inside the file `ksha256.dat` with the ave maria
5. Modify the configuration files of the other microservices (KxpHostProAPI, KtpTerminalProAPI, etc.) running on the 
embedded Linux platform to let them know the new address of the Kapri2API microservice.
To keep ssh activated run ` systemctl enable sshd.socket`
Use the command `vi` since config files can only be written by root.
   1. Http2TerminalProAPI.conf: change
      1. `url_rxinstruction = "http://127.0.0.1:12443/api/let_me_know_instruction"` to `url_rxinstruction = "http://10.0.0.144:12443/api/let_me_know_instruction"`
   2. Jso2TerminalProAPI.conf: change
      1. `api_host = "127.0.0.1"` to `api_host = "0.0.0.0"`
      2. `url_rxinstruction = "http://127.0.0.1:12443/api/let_me_know_instruction"` to `url_rxinstruction = "http://10.0.0.144:12443/api/let_me_know_instruction"`
   3. Ktp2TerminalProAPI.conf: change
      1. `api_host = "127.0.0.1"` to `api_host = "0.0.0.0"`
      2. `url_rxevent = "http://127.0.0.1:12443/api/let_me_know_event"` to `url_rxevent = "http://10.0.0.144:12443/api/let_me_know_event"`
      3. `url_rxinstruction = "http://127.0.0.1:12443/api/let_me_know_instruction"` to `url_rxinstruction = "http://10.0.0.144:12443/api/let_me_know_instruction"`
   4. Kxp2HostProAPI.conf: change
      1. `api_host = "127.0.0.1"` to `api_host = "0.0.0.0"`
      2. `api_urlrxinstruction = "http://127.0.0.1:12443/api/let_me_know_instruction"` to `api_urlrxinstruction = "http://10.0.0.144:12443/api/let_me_know_instruction"`
   5. Kapri2AssistAPI.conf: change
      1. `api_host = "127.0.0.1"` to `api_host = "0.0.0.0"`
   6. Kapri2js.conf: change
      1. `"SOCKET_HOST": "127.0.0.1"` to ` "SOCKET_HOST": "0.0.0.0"`
   7. Kapri2WebAdminjs.conf: change
      1. `"KAPRIAPI_HOST": "127.0.0.1"` to `"KAPRIAPI_HOST": "10.0.0.144"`
6. Reboot the embedded platform using `reboot now`.
7. Reconnect via Putty and stop the Kapri2API microservice on the embedded using `systemctl stop Kapri2API` and check
it using `systemctl status Kapri2API`.
8. Start the Kapri2API microservice on the Windows PC in debug mode, using the modified configuration file.


## Conclusion

Debugging Kapri2Online requires configuring the system to allow for the Kapri2API microservice to run on a PC and be debugged
in a step-by-step manner. By following the steps outlined in this document and using debugging best practices, 
developers can quickly identify and resolve issues with Kapri2API and other microservices.
