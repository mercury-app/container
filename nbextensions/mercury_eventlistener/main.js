console.log("Loading mercury event listener nbextension")

window.addEventListener('message', event => {
      // IMPORTANT: check the origin of the data!
      if (event.origin.startsWith('http://localhost')) {
          data = event.data.data;
          code = data.code
          console.log(code)

          if (data.action == "add_input_cell"){
            if (Jupyter.notebook.ncells() == 0)
                Jupyter.notebook.insert_cell_above('code').set_text(code);
            else{
                if (Jupyter.notebook.get_cell(0).get_text().startsWith("# Mercury-Input"))
                    Jupyter.notebook.get_cell(0).set_text(code);
                else
                    Jupyter.notebook.insert_cell_above('code').set_text(code);
            }
              console.log(event.data);
              console.log("cell added")
          }

          if (data.action == "add_output_cell"){
            if (Jupyter.notebook.ncells() == 0)
                Jupyter.notebook.insert_cell_below('code').set_text(code);
            else{
                if (Jupyter.notebook.get_cell(-1).get_text().startsWith("# Mercury-Output"))
                    Jupyter.notebook.get_cell(-1).set_text(code);
                else
                    Jupyter.notebook.insert_cell_below('code').set_text(code);
            }
              console.log(event.data);
              console.log("cell added")            
          }
        } else {
          console.log("BACK OFF")
          alert("message recieved")
          return;
      }
});

// frame = document.getElementById("notebook-iframe")
// frame.contentWindow.postMessage({"data":{"action": "add_input_cell", "code": "adsadadsA"}}, 
// "http://localhost:8880/notebooks/work/scripts/Untitled.ipynb");