console.log("Loading mercury event listener nbextension")

// send message to parent telling the frame url
parent.postMessage("Hello", "http://localhost:5000");

window.addEventListener('message', event => {
      // IMPORTANT: check the origin of the data!
      if (event.origin.startsWith('http://localhost')) {
          data = event.data.data;
          code = data.code
          console.log(code)

          if (data.action == "add_input_cell"){
            if (Jupyter.notebook.ncells() == 0)
                Jupyter.notebook.insert_cell_at_index('code', 0).set_text(code);
            else{
                if (Jupyter.notebook.get_cell(0).get_text().startsWith("# Mercury-Input"))
                    Jupyter.notebook.get_cell(0).set_text(code);
                else
                    Jupyter.notebook.insert_cell_at_index('code', 0).set_text(code);
            }
                Jupyter.notebook.get_cell(0)._metadata = {"trusted": true, "editable": false, 
                                                          "deletable": false}
                console.log("input cell added")
          }

          if (data.action == "add_output_cell"){
            if (Jupyter.notebook.ncells() == 0)
                Jupyter.notebook.insert_cell_at_bottom('code').set_text(code);
            else{
                if (Jupyter.notebook.get_cell(-1).get_text().startsWith("# Mercury-Output"))
                    Jupyter.notebook.get_cell(-1).set_text(code);
                else
                    Jupyter.notebook.insert_cell_at_bottom('code').set_text(code);
            }
                Jupyter.notebook.get_cell(-1)._metadata = {"trusted": true, "editable": false, 
                                                           "deletable": false}
                console.log("output cell added")            
          }
        } else {
          console.log("BACK OFF")
          alert("message recieved")
          return;
      }
});
