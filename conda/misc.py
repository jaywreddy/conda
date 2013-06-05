# this module contains miscellaneous stuff which enventually could be moved
# into other places
import os
import sys
import shutil
from subprocess import check_call
from collections import defaultdict
from os.path import abspath, basename, join

import config
import install
from plan import RM_EXTRACTED, EXTRACT, UNLINK, LINK, execute_actions



def install_local_packages(prefix, paths, verbose=False):
    # copy packages to pkgs dir
    dists = []
    for src_path in paths:
        assert src_path.endswith('.tar.bz2')
        fn = basename(src_path)
        dists.append(fn[:-8])
        dst_path = join(config.pkgs_dir, fn)
        if abspath(src_path) == abspath(dst_path):
            continue
        shutil.copyfile(src_path, dst_path)

    actions = defaultdict(list)
    actions['PREFIX'] = prefix
    actions['op_order'] = RM_EXTRACTED, EXTRACT, UNLINK, LINK
    for dist in dists:
        actions[RM_EXTRACTED].append(dist)
        actions[EXTRACT].append(dist)
        if install.is_linked(prefix, dist):
            actions[UNLINK].append(dist)
        actions[LINK].append(dist)
    execute_actions(actions, verbose=verbose)


def launch(fn, prefix=config.root_dir, additional_args=None):
    from api import get_index

    index = get_index()
    info = index[fn]

    # prepend the bin directory to the path
    fmt = r'%s\Scripts;%s' if sys.platform == 'win32' else '%s/bin:%s'
    env = {'PATH': fmt % (abspath(prefix), os.getenv('PATH'))}
    # copy existing environment variables, but not anything with PATH in it
    for k, v in os.environ.iteritems():
        if 'PATH' not in k:
            env[k] = v
    # allow updating environment variables from metadata
    if 'app_env' in info:
        env.update(info['app_env'])
    # call the entry command
    args = info['app_entry'].split()
    if additional_args:
        args.extend(additional_args)
    check_call(args, env=env)


if __name__ == '__main__':
    launch('spyder-app-2.2.0-py27_0.tar.bz2')