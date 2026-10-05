console.log("i belive in you")
// document.addEventListener("keydown", (event) => {console.log(event.key)});
//document.addEventListener("keydown", (event) => {if (/^[a-z]$/i.test(event.key)) {console.log(event.key)}});

const tiles = document.querySelectorAll(".tile");

document.addEventListener("keydown", (event) => {
    if (/^[a-z]$/i.test(event.key)) {
        tiles[0].textContent = event.key;
    }
});