console.log("i belive in you")

const message = document.getElementById("message");
const overlay = document.getElementById("overlay");
let gameOver = false;

const rows = document.querySelectorAll(".row");
let currentRow = 0;
let currentCol = 0;

document.addEventListener("keydown", (event) => {
    if (gameOver) return;
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

                    if (data.won) {
                        message.textContent = "You Won!";
                        gameOver = true;
                        overlay.style.display = "flex";
                    } else if (data.answer) {
                        message.textContent = "Game over. The word was " + data.answer;
                        gameOver = true;
                        overlay.style.display = "flex";
                    }

                    currentRow++;
                    currentCol = 0;
                }
            });
        }
    }
});

document.getElementById("restart").addEventListener("click", () => {
    location.reload();
});