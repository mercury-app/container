import click
import json
import os
import jupyter_client

from container.constants import DEFAULT_NOTEBOOK_DIR_PATH, JUPYTER_RUNTIME_DIR


class NotebookKernel:
    def __init__(self):
        json_file = [
            _
            for _ in os.listdir(JUPYTER_RUNTIME_DIR)
            if os.path.splitext(_)[1] == ".json" and _.split("-")[0] == "kernel"
        ]

        assert len(json_file) == 1, "no/two kernel jsons found"

        cf = jupyter_client.find_connection_file(json_file[0])
        self._kernel_manager = jupyter_client.BlockingKernelClient(connection_file=cf)
        self._kernel_manager.load_connection_file()

    def execute_code(self, code) -> dict:
        io_msg_id = self._kernel_manager.execute(code)

        traceback = None
        shell_msg = self._kernel_manager.get_shell_msg()
        run_status = shell_msg["content"].get("status")
        if run_status == "error":
            traceback = shell_msg["content"].get("traceback")

        return {
            "io_msg_id": io_msg_id,
            "status": run_status,
            "traceback": traceback,
        }
