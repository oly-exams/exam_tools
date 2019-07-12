import os
import sys
import io
import tempfile
import shutil
from functools import partial

from mkdocs import config
from mkdocs.exceptions import ConfigurationError
from mkdocs.plugins import BasePlugin
from mkdocs.commands import build
from mkdocs.commands import serve
from mkdocs.structure import pages
from mkdocs.utils import urlparse
from mkdocs.utils import urlunparse

import markdown
from markdown.util import AMP_SUBSTITUTE

from mkdocs.structure.toc import get_toc



class _RelativePathTreeprocessor(pages._RelativePathTreeprocessor):
    def __init__(self, file, files, config):
        self.file = file
        self.files = files
        self.config = config

    def path_to_url(self, url):
        scheme, netloc, path, params, query, fragment = urlparse(url)

        if (scheme or netloc or not path or url.startswith('/')
                or AMP_SUBSTITUTE in url or '.' not in os.path.split(path)[-1]):
            # Ignore URLs unless they are a relative link to a source file.
            # AMP_SUBSTITUTE is used internally by Markdown only for email.
            # No '.' in the last part of a path indicates path does not point to a file.
            return url

        # Determine the filepath of the target.
        target_path = os.path.join(os.path.dirname(self.file.src_path), path)
        target_path = os.path.normpath(target_path).lstrip(os.sep)

        # Validate that the target exists in files collection.
        if target_path not in self.files:
            # XXX: modified from mkdocs source:
            target_path = os.path.normpath(os.path.relpath(
                os.path.join(self.config['docs_dir'], target_path),
                self.config['event_folder_path'],
            ))
            if target_path not in self.files:
                return url
        target_file = self.files.get_file_from_path(target_path)
        path = target_file.url_relative_to(self.file)
        components = (scheme, netloc, path, params, query, fragment)
        return urlunparse(components)


class _RelativePathExtension(pages._RelativePathExtension):
    def __init__(self, file, files, config):
        self.file = file
        self.files = files
        self.config = config

    def extendMarkdown(self, md, md_globals):
        relpath = _RelativePathTreeprocessor(self.file, self.files, self.config)
        md.treeprocessors.add("relpath", relpath, "_end")




def render(self, config, files):
    """
    Convert the Markdown source file to HTML as per the config.
    """

    extensions = [
        _RelativePathExtension(self.file, files, config)
    ] + config['markdown_extensions']

    md = markdown.Markdown(
        extensions=extensions,
        extension_configs=config['mdx_configs'] or {}
    )
    self.content = md.convert(self.markdown)
    self.toc = get_toc(getattr(md, 'toc', ''))



class OverrideFilesPlugin(BasePlugin):
    def on_files(self, files, config):
        if os.path.isdir(config['event_folder_path']):
            for nav_file in files:
                nav_file_name = os.path.basename(nav_file.src_path)
                override_path = os.path.join(config['event_folder_path'], nav_file.src_path)
                if os.path.isfile(override_path):
                    nav_file.abs_src_path = os.path.normpath(os.path.abspath(override_path))
                    nav_file.src_path = os.path.normpath(os.path.relpath(nav_file.abs_src_path, config['docs_dir']))
                    print('Override path: {}'.format(nav_file.src_path))
    def on_pre_page(self, page, config, *args, **kwargs):
        # Yup, monkeypatching is hacky.
        page.render = partial(render, page)




if __name__ == '__main__':
    if len(sys.argv) >= 2:
        site_dir = tempfile.mkdtemp(prefix='mkdocs_')
        def builder():
            config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mkdocs.yml')
            cfg = config.Config(schema=config.DEFAULT_SCHEMA, config_file_path=config_file_path)
            with open(config_file_path, 'rb') as config_file:
                cfg.load_file(config_file)
            errors, warnings = cfg.validate()
            if errors:
                raise ConfigurationError(str(error))
            cfg['config_file_path'] = ""
            cfg['event_name'] = sys.argv[1]
            cfg['event_folder_path'] = os.path.normpath(os.path.join(cfg['docs_dir'], '../docs_events', cfg['event_name']))
            cfg['plugins']['override_files'] = OverrideFilesPlugin()
            if len(sys.argv) >= 4 and sys.argv[2] == 'serve':
                cfg['dev_addr'] = sys.argv[3]
                cfg['site_url'] = 'http://{0}/'.format(sys.argv[3])
            build.build(cfg, live_server=(len(sys.argv) < 5 or sys.argv[4] != 'static'))
            return cfg
        config = builder()
        if len(sys.argv) >= 4 and sys.argv[2] == 'serve':
            host, port = config['dev_addr'].split(':')
            if len(sys.argv) >= 5 and sys.argv[4] == 'static':
                serve._static_server(host, port, config['site_dir'])
            else:
                serve._livereload(host, port, config, builder, config['site_dir'])


