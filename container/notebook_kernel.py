import click
import json
import os
import requests
import jupyter_client

from container.constants import JUPYTER_RUNTIME_DIR, HOST_PORT


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

    def write_kernel_variables_to_json(self, source_outputs, dest_inputs, json_fp) -> dict:
        self.execute_code("import json")
        print("import completed")

        assert len(source_outputs) == len(dest_inputs)
        json_to_write = "{"
        for source_output, dest_input in zip(source_outputs, dest_inputs):
            json_to_write += f"'{dest_input}': {source_output}, "
        json_to_write += "}"
        
        code = f"json.dump({json_to_write}, open('{json_fp}', 'w'))"
        print(f"running code -- {code}")

        return self.execute_code(code)

    def post_kernel_status(self):
        while True:
            json_file = [
                _ for _ in os.listdir(JUPYTER_RUNTIME_DIR)
                if os.path.splitext(_)[1] == ".json" and _.split("-")[0] == "kernel"
            ]

            if len(json_file) == 1:
                print("kernel start detected")
                break

        while True:

            iopub_msg = self._kernel_manager.get_iopub_msg()
            
            node_id = os.environ.get("MERCURY_NODE")
            url = f"http://host.docker.internal:{HOST_PORT}/nodes/{node_id}/notebook"

            if iopub_msg["msg_type"] == "status":
                kernel_status = iopub_msg["content"]["execution_state"]
            print('KERNEL STATUS: ', kernel_status)
            
            data = {
                    "data": {
                        "id": node_id,
                        "type": "nodes",
                        "attributes": {
                            "kernel_state": kernel_status
                        }
                    }
                }
            
            headers = {
                'Content-Type': 'application/vnd.api+json',
                'Accept': 'application/vnd.api+json'
                }
            
            response = requests.patch(url, headers=headers, json=data)
            print(response.status_code, response.json())

