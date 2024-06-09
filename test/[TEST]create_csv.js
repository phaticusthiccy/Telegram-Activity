const fs = require('fs');

const data = require("../games/process_mapping_linux.json");
const sortedKeys = Object.keys(data).sort();

let csvContent = "Executable Names,Game Name,Keyword 1,Keyword 2,Keyword 3,Keyword 4\n";

sortedKeys.forEach(key => {
    const values = data[key];
    const exe = key;
    const gameName = values[0];
    const keywords = values.slice(1, -1);
    while (keywords.length < 4) {
        keywords.push("-");
    }
    csvContent += `${exe},${gameName},${keywords[0]},${keywords[1]},${keywords[2]},${keywords[3]}\n`;
});

fs.writeFileSync('games_linux.csv', csvContent, 'utf8');
