const data = require("../games/process_mapping.json")

Object.keys(data).forEach(key => {
    if (data[key][data[key].length - 1] !== key) {
        global.games ? global.games.push(key) : global.games = [key]
        data[key][data[key].length - 1] = key
    }
})
console.clear()
global.games ? console.log(global.games.length + " games must be fixed\nGames:: " + global.games.join(", ")) : console.log("Everything looks good")