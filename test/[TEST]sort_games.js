const data = require("../games/process_mapping.json");
const fs = require("fs");
const sortedKeys = Object.keys(data).sort();
const sortedData = {};

sortedKeys.forEach(key => {
    sortedData[key] = data[key];
});
fs.writeFileSync("./process_mapping_sort.json", JSON.stringify(sortedData, null, 2));