from logging import shutdown
import click
from notebook.services.contents.filemanager import FileContentsManager as FCM
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
import os

from container.notebook_kernel import NotebookKernel
from container.constants import DEFAULT_NOTEBOOK_DIR_PATH, JUPYTER_RUNTIME_DIR


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
@click.option('--client', required=True, help="kernel client- jupyter or nbclient")
def post_kernel_status(client):

    if client == "nbclient":
        notebook_kernel = NotebookKernel(client="jupyter")
        if notebook_kernel._kernel_manager:
            notebook_kernel.shutdown_kernel()

    while True:
        kernel_not_found = True
        while kernel_not_found:
            notebook_kernel = NotebookKernel(client=client)
            if notebook_kernel._kernel_manager:
                kernel_not_found = False
                break

        notebook_kernel.post_kernel_status()
        

@cli.command()
@click.option("--notebook_path", required=True, help="path of notebook to execute")
def run_notebook(notebook_path):
    
    # shut down jupyter clients
    notebook_kernel = NotebookKernel(client="jupyter")
    if notebook_kernel._kernel_manager:
        notebook_kernel.shutdown_kernel()

    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

    try:
        ep.preprocess(nb, {'metadata': {'path': DEFAULT_NOTEBOOK_DIR_PATH}})
    except CellExecutionError:
        out = None
        msg = f"Error executing the notebook {notebook_path}.\n\n"
        print(msg)
        raise
    finally:
        print("overwriting notebook")
        with open(notebook_path, mode='w', encoding='utf-8') as f:
            nbformat.write(nb, f)


if __name__ == "__main__":
    cli()
