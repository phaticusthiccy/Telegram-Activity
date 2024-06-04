const fs = require('fs');

const data = require("../games/process_mapping.json");
const sortedKeys = Object.keys(data).sort();

let csvContent = "Executable Names,Game Name,Keywords\n";

sortedKeys.forEach(key => {
    const values = data[key];
    const exe = key;
    const gameName = values[0];
    const keywords = values.slice(1, -1).join(', ');
    csvContent += `${exe},${gameName},${keywords}\n`;
});
fs.writeFileSync('games.csv', csvContent, 'utf8');
