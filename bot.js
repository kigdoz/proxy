/*
MCriot made by n0nexist
simple minecraft spambot with support for SOCKS4, SOCKS5, HTTP, and HTTPS proxies
*/

// Libraries
const mineflayer = require("mineflayer");
const readline = require('readline').createInterface({
  input: process.stdin,
  output: process.stdout
});
const fs = require('fs');
const httpsProxyAgent = require('https-proxy-agent');
const SocksProxyAgent = require('socks-proxy-agent');

// Constants
const array = [];
const args = process.argv.slice(2);

// Function to generate random bot name
function generateRandomName() {
    const randomString = Math.random().toString(36).slice(2, 7); // Random string of 5 characters
    return `Random_bot_name_${randomString}`; // Return in the format "Random_bot_name_randomString"
}

// Function to create proxy agent based on the proxy type
function createProxyAgent(proxy) {
    const [proxyHost, proxyPort] = proxy.split(':'); // Extract proxy host and port
    const proxyUrl = `http://${proxyHost}:${proxyPort}`; // Construct the proxy URL

    // Check if the proxy is HTTP/HTTPS or SOCKS4/5 based on the URL
    if (proxy.startsWith('socks4://') || proxy.startsWith('socks5://')) {
        // SOCKS proxy (SOCKS4/5)
        return new SocksProxyAgent(proxyUrl); // Use SocksProxyAgent for SOCKS proxies
    } else if (proxy.startsWith('http://') || proxy.startsWith('https://')) {
        // HTTP/HTTPS proxy
        return new httpsProxyAgent(proxyUrl); // Use https-proxy-agent for HTTP/HTTPS proxies
    } else {
        throw new Error('Unsupported proxy type');
    }
}

// Function to manage bots
function addbot(h, p, n, v, proxy) {
    /*
    Adds a bot to the array with proxy support
    */
    const agent = createProxyAgent(proxy); // Create the appropriate proxy agent
    const botName = generateRandomName(); // Generate a random bot name
    
    array.push(mineflayer.createBot({
        host: h,
        username: botName, // Use the random bot name here
        port: parseInt(p),
        version: v,
        agent: agent // Add the proxy agent here
    }));
}

function chatall(text) {
    /*
    Makes all bots in the array send a chat message
    */
    array.forEach(function(bot) {
        bot.chat(text);
    });
}

/*
Main code
*/
if (args[4] == undefined || args[5] == undefined) {
    console.log("usage: MCriot.js (ip) (port) (bot name) (bot count) (version) (proxy list file)\nexample: MCriot.js localhost 25565 hello 10 1.8.9 proxies.txt");
    process.exit(1);
}

// Read the proxies from the file
let proxyList;
try {
    proxyList = fs.readFileSync(args[5], 'utf-8').split('\n').filter(line => line.trim() !== "");
} catch (error) {
    console.error("Error reading proxy file:", error);
    process.exit(1);
}

if (proxyList.length < parseInt(args[3])) {
    console.log("Not enough proxies for the number of bots. Please provide more proxies.");
    process.exit(1);
}

console.log("* starting", args[3], "bots against", args[0] + ":" + args[1], "using proxies from", args[5]);

// Create bots with proxies
for (let i = 0; i < parseInt(args[3]); i++) {
    const proxy = proxyList[i];
    try {
        addbot(args[0], args[1], args[2], args[4], proxy);
        console.log("+ created bot n." + (i + 1) + "/" + args[3] + " using proxy: " + proxy);
    } catch (error) {
        console.error("Error creating bot with proxy", proxy, ":", error);
    }
}

// Create last bot with chat event
const chatevent = mineflayer.createBot({
    host: args[0],
    username: generateRandomName(), // Use random name for the listener bot too
    port: parseInt(args[1]),
    version: args[4]
});

chatevent.on('chat', (username, message) => {
    if (username === chatevent.username) return;
    console.log("[CHAT]", username, "->", message);
});

console.log("* bots are joining; you can now type commands");

function promptCMD() {
    readline.question('', command => {
        console.log(`+ sending "${command}" to all bots..`);
        chatall(command); // sends command to all bots
        chatevent.chat(command); // sends the command to the last bot with chat listener
        promptCMD(); // show again the prompt for typing commands
    });
}
promptCMD();
