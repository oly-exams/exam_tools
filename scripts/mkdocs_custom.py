# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/env python

import os
import sys
import io
import tempfile
import shutil
from functools import partial
import argparse

from mkdocs import config as mk_config
from mkdocs.exceptions import ConfigurationError
from mkdocs.plugins import BasePlugin
from mkdocs.commands import build
from mkdocs.commands import serve
from mkdocs.structure import files


class OverrideFilesPlugin(BasePlugin):
    def on_files(self, nav_files, config):
        if os.path.isdir(config["event_folder_path"]):
            fs = []
            orig_rel_paths = [nav_file.src_path for nav_file in nav_files]
            for nav_file in nav_files:
                abs_path = os.path.join(config["event_folder_path"], nav_file.src_path)
                if os.path.isfile(abs_path):
                    f = files.File(
                        nav_file.src_path,
                        os.path.abspath(config["event_folder_path"]),
                        config["site_dir"],
                        config["use_directory_urls"],
                    )
                    fs.append(f)
                    print(f"Override path: {f.src_path}")
                else:
                    fs.append(nav_file)
            for folder, __, nav_new_files in os.walk(config["event_folder_path"]):
                for nav_new_file in nav_new_files:
                    nav_new_filepath = os.path.normpath(
                        os.path.relpath(
                            os.path.join(folder, nav_new_file),
                            config["event_folder_path"],
                        )
                    )
                    if nav_new_filepath not in orig_rel_paths:
                        f = files.File(
                            nav_new_filepath,
                            os.path.abspath(config["event_folder_path"]),
                            config["site_dir"],
                            config["use_directory_urls"],
                        )
                        fs.append(f)
                        print(f"New path: {f.src_path}")
            return files.Files(fs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run mkdocs with overrides.")
    parser.add_argument(
        "event_name",
        help="name of the event, corresponding to the folder to search for override files",
    )
    parser.add_argument(
        "-s", "--serve", help="run the development server", action="store_true"
    )
    parser.add_argument("-a", "--address", help="host:port of the development server")
    parser.add_argument(
        "-t",
        "--static",
        help="make the development server static instead of livereloading",
        action="store_true",
    )
    parser.add_argument("-d", "--site-dir", help="output directory")
    args = parser.parse_args()

    def builder():
        config_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mkdocs.yml"
        )
        cfg = mk_config.Config(
            schema=mk_config.defaults.get_schema(), config_file_path=config_file_path
        )
        with open(config_file_path, "rb") as config_file:
            cfg.load_file(config_file)
        if args.site_dir:
            cfg.load_dict({"site_dir": args.site_dir})
        errors, warnings = cfg.validate()
        if errors:
            raise ConfigurationError(str(errors))
        cfg["config_file_path"] = ""
        cfg["event_name"] = args.event_name
        cfg["event_folder_path"] = os.path.normpath(
            os.path.join(cfg["docs_dir"], "../docs_events", cfg["event_name"])
        )
        cfg["plugins"]["override_files"] = OverrideFilesPlugin()
        if args.address:
            cfg["dev_addr"] = args.address
            cfg["site_url"] = "http://{}/".format(cfg["dev_addr"])
        build.build(cfg, live_server=not args.static)
        return cfg

    cfg = builder()
    if args.serve:
        if args.address is None:
            host = "localhost"
            port = "8000"
        else:
            host, port = args.address.split(":")
        if args.static:
            serve._static_server(host, port, cfg["site_dir"])
        else:
            serve._livereload(host, port, cfg, builder, cfg["site_dir"])
