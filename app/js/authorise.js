function loadUrl(location) {
    console.log(location);
    window.location = location;
}
function authorise(){
    var ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        console.log(this.status + " " + this.response + " " + ajax.readyState)
        if (ajax.readyState==4 && ajax.status==200) {
            var link = "http://" + window.document.location.host + "/charge/" + this.responseText
            console.log(link)
            loadUrl(link);
        }
    }
    ajax.open("OPTIONS", "");
    ajax.send();
}
authorise()