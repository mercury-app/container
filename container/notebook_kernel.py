from nbclient import client
import click
import json
import os
import requests
import jupyter_client
import time

from container.constants import JUPYTER_RUNTIME_DIR, HOST_PORT


class NotebookKernel:
    def __init__(self, client=None):
        self._client = client if client else "jupyter"
        self._kernel_manager = None
        assert self._client in ["jupyter", "nbclient"]

        conn_file = None
        if self._client == "jupyter" and os.path.exists(JUPYTER_RUNTIME_DIR):
            json_file = [
                _
                for _ in os.listdir(JUPYTER_RUNTIME_DIR)
                if os.path.splitext(_)[1] == ".json" and _.split("-")[0] == "kernel"
            ]

            if len(json_file) == 1:
                conn_file = jupyter_client.find_connection_file(json_file[0])

        if self._client == "nbclient":
            json_files_in_tmp = [_ for _ in os.listdir('/tmp/') if os.path.splitext(_)[1] == ".json"]
            if len(json_files_in_tmp)>0:
                for json_file in json_files_in_tmp:
                    try:
                        with open(f"/tmp/{json_file}") as f:
                            keys_in_json = json.load(f).keys()
                            if "kernel_name" in keys_in_json:
                                conn_file = f"/tmp/{json_file}"
                                break
                    except:
                        print("no nbclient exits")
                        continue
                
        if conn_file:
            print(f"connection file for kernel found at {conn_file}")
            self._kernel_manager = jupyter_client.BlockingKernelClient(connection_file=conn_file)
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
            iopub_msg = self._kernel_manager.get_iopub_msg()

            if "msg_type" in iopub_msg["parent_header"]:
                if iopub_msg["parent_header"]["msg_type"] == "shutdown_request":
                    print("Kernel shutdown detected")
                    # sleep because jupyter takes time in shutting down container
                    time.sleep(3)
                    kernel_shutdown = True
                    return kernel_shutdown

            node_id = os.environ.get("MERCURY_NODE")
            url = f"http://host.docker.internal:{HOST_PORT}/nodes/{node_id}/notebook"

            if iopub_msg["msg_type"] == "status":
                kernel_status = iopub_msg["content"]["execution_state"]
            print('kernel client: ', self._client)
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


    def shutdown_kernel(self):
        self._kernel_manager.shutdown()