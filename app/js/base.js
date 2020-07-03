function Redirect() {
    if (window.location.pathname !== "/") {
        window.location = "/";
    }
}

function loadUrl(location) {
    console.log(location);
    window.location = location;
}

const sleep = (milliseconds) => {
    return new Promise(resolve => setTimeout(resolve, milliseconds))
}

setTimeout('Redirect()', 30000);
