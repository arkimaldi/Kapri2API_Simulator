# (C) 2023 Kimaldi Electronics,s.l. <www.kimaldi.com>. All rights reserved.

import os
import sys

try:
    print('###################################################')
    print('###############  KAPRI2API  START  ################')
    print('###################################################')

    app_mode = os.getenv('APP_MODE') or 'normal'
    if app_mode == 'normal':
        try:
            import argparse
            import constants

            # determinem el fitxer de configuració a usar
            config_file_route = os.path.join(constants.CONFIG_DIRNAME_DEFAULT, constants.CONFIG_FILENAME_DEFAULT)

            parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
            parser.add_argument(
                '-c', '--config',
                dest='config',
                type=str,
                help='configuration file name',
                default=config_file_route,
            )

            args = parser.parse_args()

            if args.config != config_file_route:
                config_file_route = args.config
                if not os.path.isfile(config_file_route):
                    parser.error("Invalid configuration file")
            else:
                if not os.path.isfile(config_file_route):
                    parser.error("Invalid default configuration file")

            print(f'{config_file_route} selected as configuration file', flush=True)
        except Exception as e:
            print(f'Exception selecting configuration file: {str(e)}', flush=True)
            sys.exit(1)
        else:
            # carreguem configuració
            try:
                # carreguem configuració
                from cfg_loader import CfgLoader
                CfgLoader.load_cfg_file(config_file_route)
            except Exception as e:
                print(f'Exception loading configuration file: {str(e)}', flush=True)
                sys.exit(1)
            else:
                try:
                    # instanciem app (incorpora l'aplicació KapriAPP)
                    from app import create_app
                    app = create_app(config_name='waitress')

                    from waitress import serve
                    api_host = app.config['API']['api_host']
                    api_port = app.config['API']['api_port']
                    print(f'Starting server at {api_host}:{api_port}', flush=True)
                    serve(app, host=api_host, port=api_port)
                except Exception as e:
                    print(f'Exception launching the server: {str(e)}')
                    sys.exit(1)
    elif app_mode == 'maintenance':
        # carreguem configuració
        try:
            # determinem el fitxer de configuració
            import constants
            config_file_route = os.path.join(constants.CONFIG_DIRNAME_DEFAULT, constants.CONFIG_FILENAME_DEFAULT)

            # carreguem configuració
            from cfg_loader import CfgLoader
            CfgLoader.load_cfg_file(config_file_route)
        except Exception as e:
            print(f'Exception loading configuration file: {str(e)}', flush=True)
        else:
            import sys
            import unittest
            import click
            from flask.cli import FlaskGroup
            from app import create_app

            app = create_app(config_name='waitress', do_start=False)

            @click.group(cls=FlaskGroup, create_app=lambda: app)
            def cli():
                """Management script for KapriCloudMainAPI application."""

            @app.cli.command()
            def test():
                """Run the unit tests."""
                if not app.config.get('TESTING'):
                    sys.exit("Error: Not running unit tests with a testing configuration")

                with app.app_context():
                    tests = unittest.TestLoader().discover('tests')
                    unittest.TextTestRunner(verbosity=2).run(tests)

            cli()

    elif app_mode == 'test':
        import sys
        import unittest
        import click
        from flask.cli import FlaskGroup
        from app import create_app

        app = create_app(config_name='testing', do_start=False)

        @click.group(cls=FlaskGroup, create_app=lambda: app)
        def cli():
            """Management script for KapriCloudMainAPI application."""

        @app.cli.command()
        def test():
            """Run the unit tests."""
            if not app.config.get('TESTING'):
                sys.exit("Error: Not running unit tests with a testing configuration")

            with app.app_context():
                tests_directory = os.path.join('src', 'tests')
                tests = unittest.TestLoader().discover(tests_directory)
                unittest.TextTestRunner(verbosity=2).run(tests)

        cli()

    else:
        print('Error: Unknown APP_MODE')
        sys.exit(1)
except Exception as e:
    print(f'Exception starting Kapri2API: {str(e)}')
    sys.exit(1)
finally:
    print('###############  KAPRI2API EXIT  ##################')
