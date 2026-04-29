import ast
import os

from PyInstaller.utils import hooks


def _collect_lazy_imports_from_handlers():
    """Parse handlers.py with AST to extract module paths from
    LazyCommand (3rd arg) and lazy_callback (1st arg) calls.
    """
    handlers_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'awscli', 'handlers.py'
    )
    with open(handlers_path) as f:
        tree = ast.parse(f.read())
    modules = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name == 'LazyCommand' and len(node.args) >= 3:
            arg = node.args[2]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                modules.add(arg.value)
        elif name == 'lazy_callback' and len(node.args) >= 1:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                modules.add(arg.value)
    return sorted(modules)

hiddenimports = [
    'docutils',
    'urllib',
    'httplib',
    'html.parser',
    'configparser',
    'xml.etree',
    'pipes',
    'colorama',
    'awscli.handlers',
    # NOTE: This can be removed once this hidden import issue related to
    # setuptools and PyInstaller is resolved:
    # https://github.com/pypa/setuptools/issues/1963
    'pkg_resources.py2_warn',
]

imports_for_legacy_plugins = hooks.collect_submodules(
    'http'
) + hooks.collect_submodules('logging')
hiddenimports += imports_for_legacy_plugins

alias_packages_plugins = hooks.collect_submodules(
    'awscli.botocore'
) + hooks.collect_submodules('awscli.s3transfer')
hiddenimports += alias_packages_plugins

# Lazy-loaded modules in handlers.py are not discovered by PyInstaller's
# static analysis. Parse the source to collect them automatically.
hiddenimports += _collect_lazy_imports_from_handlers()


# Completion model files are only used at build time to generate the
# ac.index SQLite database. They are not needed at runtime and can be
# excluded to reduce the size of the PyInstaller distribution.
EXCLUDED_DATA_FILE_BASENAMES = {
    'completions-1.json',
    'completions-1.sdk-extras.json',
}


datas = [
    (src, dest)
    for src, dest in hooks.collect_data_files('awscli')
    if os.path.basename(src) not in EXCLUDED_DATA_FILE_BASENAMES
]


# prompt_toolkit uses its own metadata to determine
# its version. So we need to bundle the package
# metadata to avoid runtime errors.
# https://github.com/aws/aws-cli/issues/9453
datas += hooks.copy_metadata('prompt_toolkit')
