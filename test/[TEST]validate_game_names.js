const data = require("../games/process_mapping.json")

Object.keys(data).forEach(key => {
    if (data[key][data[key].length - 1] !== key) {
        console.warn("" + key + " is not the last element in the array")
        data[key][data[key].length - 1] = key
    }
})