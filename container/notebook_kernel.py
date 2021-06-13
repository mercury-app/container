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
            print(traceback)

        return {
            "io_msg_id": io_msg_id,
            "status": run_status,
            "traceback": traceback,
        }

    def write_kernel_variables_to_json(self, variables, json_fp) -> dict:
        self.execute_code("import json")
        print("import completed")

        json_to_write = "{"
        for variable in variables:
            json_to_write += f"'{variable}': {variable}, "
        json_to_write += "}"
        
        code = f"json.dump({json_to_write}, open('{json_fp}', 'w'))"
        print(f"running code -- {code}")

        return self.execute_code(code)
