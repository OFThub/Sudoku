let size, sr, sc;
let board = [];
let inputs = [];

function isValid(board, r, c, val) {
    for (let i = 0; i < size; i++) {
        if (board[r][i] === val || board[i][c] === val) return false;
    }

    let br = Math.floor(r / sr) * sr;
    let bc = Math.floor(c / sc) * sc;

    for (let i = br; i < br + sr; i++)
        for (let j = bc; j < bc + sc; j++)
            if (board[i][j] === val) return false;

    return true;
}

function solve(board) {
    for (let r = 0; r < size; r++) {
        for (let c = 0; c < size; c++) {
            if (board[r][c] === 0) {
                let nums = [...Array(size).keys()].map(n => n + 1);
                nums.sort(() => Math.random() - 0.5);

                for (let n of nums) {
                    if (isValid(board, r, c, n)) {
                        board[r][c] = n;
                        if (solve(board)) return true;
                        board[r][c] = 0;
                    }
                }
                return false;
            }
        }
    }
    return true;
}

function generateSudoku(diff) {
    sr = size === 6 ? 2 : 3;
    sc = 3;

    board = Array.from({ length: size }, () => Array(size).fill(0));
    solve(board);

    let ratio = { "Kolay": 0.55, "Orta": 0.4, "Zor": 0.28 }[diff];
    let keep = Math.floor(size * size * ratio);

    let cells = [];
    for (let r = 0; r < size; r++)
        for (let c = 0; c < size; c++)
            cells.push([r, c]);

    cells.sort(() => Math.random() - 0.5);
    for (let i = keep; i < cells.length; i++) {
        let [r, c] = cells[i];
        board[r][c] = 0;
    }
}

function startGame() {
    size = parseInt(document.getElementById("size").value);
    let cellSize = parseInt(document.getElementById("cellSize").value);
    let diff = document.getElementById("difficulty").value;

    generateSudoku(diff);
    drawBoard(cellSize);
}

function drawBoard(cellSize) {
    const game = document.getElementById("game");
    game.innerHTML = "";
    inputs = [];

    game.className = "";
    game.classList.add(size === 6 ? "sudoku-6" : "sudoku-9");

    for (let r = 0; r < size; r++) {
        let row = document.createElement("div");
        row.className = "row";
        inputs[r] = [];

        for (let c = 0; c < size; c++) {
            let input = document.createElement("input");
            input.className = "cell";
            input.style.width = cellSize + "px";
            input.style.height = cellSize + "px";
            input.style.fontSize = cellSize / 2 + "px";
            input.maxLength = 1;

            if (board[r][c] !== 0) {
                input.value = board[r][c];
                input.disabled = true;
                input.classList.add("fixed");
            }

            input.oninput = () => {
                if (!/^[1-9]$/.test(input.value) || input.value > size) {
                    input.value = "";
                }
                check();
            };

            row.appendChild(input);
            inputs[r][c] = input;
        }
        game.appendChild(row);
    }
}

function getVal(r, c) {
    let v = inputs[r][c].value;
    return /^\d+$/.test(v) ? parseInt(v) : 0;
}

function check() {
    let valid = Array.from({ length: size }, () => Array(size).fill(true));

    inputs.flat().forEach(i => i.classList.remove("valid", "invalid"));

    // Satırlar
    for (let r = 0; r < size; r++) {
        let seen = {};
        for (let c = 0; c < size; c++) {
            let v = getVal(r, c);
            if (v && seen[v] !== undefined) {
                valid[r][c] = valid[r][seen[v]] = false;
            }
            seen[v] = c;
        }
    }

    // Sütunlar
    for (let c = 0; c < size; c++) {
        let seen = {};
        for (let r = 0; r < size; r++) {
            let v = getVal(r, c);
            if (v && seen[v] !== undefined) {
                valid[r][c] = valid[seen[v]][c] = false;
            }
            seen[v] = r;
        }
    }

    // Kutular
    for (let br = 0; br < size; br += sr) {
        for (let bc = 0; bc < size; bc += sc) {
            let seen = {};
            for (let r = br; r < br + sr; r++)
                for (let c = bc; c < bc + sc; c++) {
                    let v = getVal(r, c);
                    if (v && seen[v]) {
                        let [pr, pc] = seen[v];
                        valid[r][c] = valid[pr][pc] = false;
                    }
                    seen[v] = [r, c];
                }
        }
    }

    // Renklendirme
    let solved = true;

    for (let r = 0; r < size; r++) {
        for (let c = 0; c < size; c++) {
            if (inputs[r][c].disabled) continue;
            let v = getVal(r, c);
            if (!v) solved = false;
            else if (!valid[r][c]) {
                inputs[r][c].classList.add("invalid");
                solved = false;
            }
        }
    }

    // Doğru satır
    for (let r = 0; r < size; r++)
        if (inputs[r].every((_, c) => getVal(r, c) && valid[r][c]))
            inputs[r].forEach(i => i.classList.add("valid"));

    // Doğru sütun
    for (let c = 0; c < size; c++) {
        let col = inputs.map(r => r[c]);
        if (col.every((_, r) => getVal(r, c) && valid[r][c]))
            col.forEach(i => i.classList.add("valid"));
    }

    // Doğru kutu
    for (let br = 0; br < size; br += sr)
        for (let bc = 0; bc < size; bc += sc) {
            let cells = [];
            for (let r = br; r < br + sr; r++)
                for (let c = bc; c < bc + sc; c++)
                    cells.push([r, c]);

            if (cells.every(([r, c]) => getVal(r, c) && valid[r][c]))
                cells.forEach(([r, c]) => inputs[r][c].classList.add("valid"));
        }

    if (solved) alert("🎉 Sudokuyu çözdünüz!");
}
