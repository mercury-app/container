console.log("MERCURY EXTENSION LOADED")

window.addEventListener('message', event => {
      // IMPORTANT: check the origin of the data!
      if (event.origin.startsWith('http://localhost')) {
          data = event.data.data;
          
          if data.action == "add_input_cell"{
              var cell = document.getElementsByClassName("code_cell")[0];
              var cell_add = cell.cloneNode(true)
              document.getElementById("notebook-container").prepend(cell_add)
              console.log(event.data);
              alert("message recieved")
          }


         
        } else {
          console.log("BACK OFF")
          alert("message recieved")
          return;
      }
});

// frame.contentWindow.postMessage({"data":{"action": "add_input_cell", "code": "adsadadsA"}}, 
// "http://localhost:8880/notebooks/work/scripts/Untitled.ipynb");