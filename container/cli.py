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
@click.option("--source_outputs", required=True, help="pipe separated list of input variables whose values will be written")
@click.option("--dest_inputs", required=True, help="pipe separated list of variable names that will be written in the json as keys")
@click.option("--json", required=True, help="json file path")
def write_kernel_variables_to_json(source_outputs, dest_inputs, json):
    notebook_kernel = NotebookKernel()
    source_outputs = [_.strip() for _ in source_outputs.split("|")]
    dest_inputs = [_.strip() for _ in dest_inputs.split("|")]
    notebook_kernel.write_kernel_variables_to_json(source_outputs, dest_inputs, json)

@cli.command()
def post_kernel_status():
    noteboook_kernel = NotebookKernel()
    noteboook_kernel.post_kernel_status()


if __name__ == "__main__":
    cli()
