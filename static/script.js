console.log("i belive in you")
// document.addEventListener("keydown", (event) => {console.log(event.key)});
//document.addEventListener("keydown", (event) => {if (/^[a-z]$/i.test(event.key)) {console.log(event.key)}});

const rows = document.querySelectorAll(".row");
let currentRow = 0;
let currentCol = 0;

document.addEventListener("keydown", (event) => {
    if (/^[a-z]$/i.test(event.key) && currentCol < 5) {
        const rowTiles = rows[currentRow].children;
        rowTiles[currentCol].textContent = event.key;
        currentCol++;
    }

    if (event.key === "Backspace") {
        if (currentCol > 0) {
            currentCol--;
            const rowTiles = rows[currentRow].children;
            rowTiles[currentCol].textContent = "";
        }
    }

    if (event.key === "Enter") {
        if (currentCol > 4) {
            const rowTiles = rows[currentRow].children;
            let word = "";
            for (const tile of rowTiles) {
                word += tile.textContent;
            }
            
            fetch("/guess", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({guess: word})
            })

            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    for (let i = 0; i < 5; i++) {
                        rowTiles[i].classList.add(data.result[i]);
                    }
                    currentRow++;
                    currentCol = 0;
                }
            });

        }
    }
});



