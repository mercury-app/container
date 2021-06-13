import click
from notebook.services.contents.filemanager import FileContentsManager as FCM

from container.notebook_kernel import NotebookKernel
from container.constants import DEFAULT_NOTEBOOK_DIR_PATH


@click.group()
def cli():
    click.echo("Starting container interactions")


@cli.command()
@click.option("--name", default="Untitled.ipynb", help="name of notebook file")
def create_notebook(name):
    notebook_path = f"{DEFAULT_NOTEBOOK_DIR_PATH}/{name}"
    FCM().new(path=notebook_path)


@cli.command()
@click.option("--code", help="code block to execute")
def execute_code(code):
    notebook_kernel = NotebookKernel()
    notebook_kernel.execute_code(code)

@cli.command()
@click.option("--variables", help="pipe separated list of variables")
@click.option("--json", help="json file path")
def write_kernel_variables_to_json(variables, json):
    notebook_kernel = NotebookKernel()
    variables = [_.strip() for _ in variables.split("|")]
    notebook_kernel.write_kernel_variables_to_json(variables, json)


if __name__ == "__main__":
    cli()
